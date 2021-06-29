#!/usr/bin/env python
from avocado import Test
import subprocess
from subprocess import Popen, PIPE
import os, re
import systeminfo
from systeminfo import Run

########################################
# Module Name = check_threshold_handler.py
# Description: Check if thresholding interrupt handler is installed
########################################

class MceTest(Test):
    def test_MCA_thresholding_inthandler_installed(self):

        # Check if PFEH is disabled
        # A valid threshold counter present and not locked
        code, out_MCA_MISC, err = systeminfo.Run(["rdmsr 0xc0002003"])
        if ((int(out_MCA_MISC, 16) >> 61) & 7 != 6):
            self.fail("PFEH is not disabled")
    
        # Check in dmesg for APIC LVT 510
        dmesg_info = Popen(["dmesg"], stdout=PIPE, universal_newlines=True)
        kern_msg = Popen(["grep", "LVT"], stdin=dmesg_info.stdout, stdout=PIPE,
                universal_newlines=True).communicate()[0]
        dmesg_info.stdout.close()

        if "LVT offset 1 assigned for vector 0xf9" in kern_msg:
            self.log.info("MCA Thresholding interrupt handler is installed")

            # Check for appropriate vector value for APIC 510 across all CPUs
            code, num_cpus, err = systeminfo.Run(["nproc"])
            for cpu in range(0, int(num_cpus)):
                code, out_APIC510, err = systeminfo.Run(["rdmsr -p %s 0x0851" % (cpu)])

                if int(out_APIC510, 16) != 0xf9:
                    self.fail("APIC 510 is not written with appropriate vector value for cpu %d",
                            cpu)
        
        else:
            self.fail("MCA Thresholding interrupt handler is not installed")

if __name__ == "__main__":
    main()
