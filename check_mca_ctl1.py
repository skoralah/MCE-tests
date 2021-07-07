#!/usr/bin/env python

from avocado import Test
import subprocess
from subprocess import Popen, PIPE
import os, re
import systeminfo
from systeminfo import *
########################################
# Module Name: check_mca_ctl
# Description: This a simple test to check if MCA_CTL register has enabled
#              error reporting for all available errors corresponding to
#              each block across all logical CPUs
########################################

# Dictionary of available errors for each bank.
# This dictionary includes ZP, SSP and GN.
# Extend for future families.
dict_banks = {0 : ['21', '21', '24'], 1: ['14', '14', '19'],
        2: ['4', '4', '4'], 3: ['9', '9', '10'], 5: ['11', '12', '14'],
        6: ['7', '7', '7'], 7: ['8', '8', '8'], 8: ['8', '8', '8'],
        9: ['8', '8', '8'], 10: ['8', '8', '8'], 11: ['8', '8', '8'],
        12: ['8', '8', '8'], 13: ['8', '8', '8'], 14: ['8', '8', '8'],
        15: ['6', '10', '10'], 16: ['6', '1', '1'], 17: ['1', '8', '17'],
        18: ['1', '8', '17'], 19: ['1', '14', '14'], 20: ['9', '14', '14'],
        21: ['9', '0', '0'], 22: ['4', '5', '5'], 23: ['0', '5', '5'],
        24: ['0', '11', '11'], 25: ['0', '18', '18'], 26: ['0', '1', '1'],
        27: ['0', '5', '5']}

class McemcactlTest(Test):
    def test_MCA_CTL_programmed_correctly(self):

        # Get family info
        eq_id = int(systeminfo.get_current_equivalent_id(), 16)

        # Calculate family from Equivalent ID
        # Family = BaseFamily[3:0]+ExtendedFamily[7:0]
        base_fam = (eq_id >> 8) & 0xf
        extended_fam = (eq_id >> 20) & 0xff
        family = hex(base_fam + extended_fam)

        # Calculate Model from Equivalent ID
        # Model = ExtendedModel[:0],BaseModel[3:0]
        base_model = hex((eq_id >> 4) & 0xf)[2:]
        extended_model = hex((eq_id >> 16) & 0xf)[2:]
        model = hex(int(extended_model + base_model, 16))

        # Get total number of cpus
        code, num_cpus, err = systeminfo.Run(["nproc"])
        for cpu in range(0, int(num_cpus)):
            code, out_MCG_CAP, err = systeminfo.Run(["rdmsr -p %s 0x00000179"
                % (cpu)])

            # Extract MCG_CAP[0:7] to get number of error reporting banks
            out_MCG_CAP = int(out_MCG_CAP, 16) & 0xff

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

                # Read MCA_CTL register value across all banks and cpus
                # MCA_CTL register index = 0
                MCA_CTL_address = 0xc0002000 + (0x10 * bank)
                code, out_MCA_CTL, err = systeminfo.Run(["rdmsr -p %s %s"
                    % (cpu, hex(MCA_CTL_address))])

                # Get the mask of enable bits for each bank on each CPU
                # ZP
                if int(family, 16) == int("0x17", 16) and int(model, 16)\
                        in range(0x00, 0x0f):
                    mask_MCA_CTL = ((1 << int(dict_banks[bank][0])) - 1)

                # SSP
                elif int(family, 16) == int("0x17", 16) and int(model, 16)\
                        in range(0x30, 0x3f):
                    mask_MCA_CTL = ((1 << int(dict_banks[bank][1])) - 1)

                # GN
                elif int(family, 16) == int("0x19", 16) and int(model, 16)\
                        in range (0x00, 0x0f):
                    mask_MCA_CTL = ((1 << int(dict_banks[bank][2])) - 1)

                # If the mask of set bits is not equal to MCA_CTL register
                # value read then fail the test!
                if int(out_MCA_CTL, 16) != mask_MCA_CTL:
                    self.fail(out_MCA_CTL)

if __name__ == "__main__":
    main()
