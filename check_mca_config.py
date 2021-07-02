#!/usr/bin/env python
from avocado import Test
import subprocess
from subprocess import Popen, PIPE
import os, re
import systeminfo
from systeminfo import *

zp_eqid = ['0x00800f00', '0x00800f11', '0x00800f12']
ssp_eqid = ['0x00830f00', '0x00830f10']
gn_eqid = ['0x00a00f00']

NUM_BANKS_SSP_GN = 27
NUM_BANKS_ZP = 22
########################################
# Module Name: check_mca_config
# Description: This module tests if MCA_CONFIG[McaXEnable] = 1
#              and MCA_CONFIG[DeferredIntType] = 01b
#              whereas other fields are at "Reset" or "Init: BIOS" values.
########################################
class MceTest(Test):
    def test_MCA_CONFIG_programmed_correctly(self):

        # Get family info
        eq_id = systeminfo.get_current_equivalent_id()

        # Get total number of cpus
        code, num_cpus, err = systeminfo.Run(["nproc"])
        for cpu in range(0, int(num_cpus)):

            # For SSP and GN
            if (eq_id in ssp_eqid or eq_id in gn_eqid):
                num_of_banks = NUM_BANKS_SSP_GN
            elif eq_id in zp_eqid:
                num_of_banks = NUM_BANKS_ZP

            for bank in range(num_of_banks + 1):

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
