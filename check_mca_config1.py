#!/usr/bin/env python
from avocado import Test
import subprocess
from subprocess import Popen, PIPE
import os, re
import systeminfo
from systeminfo import *

########################################
# Module Name: check_mca_config
# Description: This module tests if MCA_CONFIG[McaXEnable] = 1 and
#              MCA_CONFIG[DeferredIntType] = 01b whereas other fields
#              are at "Reset" or "Init: BIOS" values, across all banks
#              for each logical CPU.
########################################
class MceTest(Test):
    def test_MCA_CONFIG_programmed_correctly(self):

        # Get total number of cpus
        code, num_cpus, err = systeminfo.Run(["nproc"])
        for cpu in range(0, int(num_cpus)):
            code, out_MCG_CAP, err = systeminfo.Run(["rdmsr -p %s 0x00000179"
                % (cpu)])

            # Extract MCG_CAP[0:7] to get number of error reporting banks
            out_MCG_CAP = int(out_MCG_CAP[1:], 16)

            # Check for all available banks for the current cpu
            for bank in range(out_MCG_CAP + 1):

                # Address = SMCA base + (0x10 * bank number) + register index
                # MCA_IPID register index = 5
                MCA_IPID_address = 0xc0002000 + (0x10 * bank) + 0x05
                code, out_MCA_IPID, err = systeminfo.Run(["rdmsr -p %s %s"
                    % (cpu, hex(MCA_IPID_address))])

                # If MCA_IPID is zero, nothing in the bank
                # Continue execution with the next bank
                if int(out_MCA_IPID, 16) == 0:
                    continue

                # Read MCA_CONFIG register value across all banks and cpus
                # MCA_CONFIG register index = 4
                MCA_CONFIG_address = 0xc0002000 + (0x10 * bank) + 0x04
                code, out_MCA_CONFIG, err = systeminfo.Run(["rdmsr -p %s %s"
                    % (cpu, hex(MCA_CONFIG_address))])

                # Check for McaXEnable
                if ((int(out_MCA_CONFIG, 16) >> 32) & 1 != 1):
                    self.fail("MCA_CONFIG[McaXEnable] is not set to 1")

                # Check for DeferredIntType
                if ((int(out_MCA_CONFIG, 16) >> 37) & 3 != 1):
                    self.fail("MCA_CONFIG[DeferredIntType] is not set to 01b")

if __name__ == "__main__":
    main()
