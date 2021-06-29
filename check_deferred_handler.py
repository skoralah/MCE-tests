#!/usr/bin/env python
from avocado import Test
import subprocess
from subprocess import Popen, PIPE
import os, re
import systeminfo
from systeminfo import Run

########################################
# Module Name = check_deferred_handler
# Description: Check if deferred error interrupt handler is installed
########################################

class MceTest(Test):
    def test_deferred_err_inthandler_installed(self):
        """
        Check for dmesg and vector value read from APIC520
        """
        # Check in dmesg for APIC LVT 520
        dmesg_info = Popen(["dmesg"], stdout=PIPE, universal_newlines=True)
        kern_msg = Popen(["grep", "LVT"], stdin=dmesg_info.stdout, stdout=PIPE,
                universal_newlines=True).communicate()[0]
        dmesg_info.stdout.close()

        if "LVT offset 2 assigned for vector 0xf4" in kern_msg:
            self.log.info("Deferred error interrupt handler is installed")

            # Check for appropriate vector value for APIC 520 across all CPUs
            code, num_cpus, err = systeminfo.Run(["nproc"])
            for cpu in range(0, int(num_cpus)):
                code, out_APIC520, err = systeminfo.Run(["rdmsr -p %s 0x0852" % (cpu)])

                if int(out_APIC520, 16) != 0xf4:
                    self.fail("APIC 520 is not written with appropriate vector value for cpu %d",
                            cpu)
        else:
            self.fail("Deferred error interrupt handler is not installed")

if __name__ == "__main__":
    main()
