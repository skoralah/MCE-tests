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

# Equivalent IDs for SSP, GN, ZP
# Extend it for future processors by adding corresponding equivalent IDs
zp_eqid = ['0x00800f00', '0x00800f11', '0x00800f12']
ssp_eqid = ['0x00830f00', '0x00830f10']
gn_eqid = ['0x00a00f00', '0x00a00f10']

# Dictionary of MCA bank numbers and number of enable bits to be set for
# each MCA bank control register
dict_banks_SSP_GN = {0 : ['21', '24'], 1: ['14', '19'], 2: ['4', '4'],
        3: ['9', '10'], 5: ['12', '14'], 6: ['7', '7'], 7: ['8', '8'],
        8: ['8', '8'], 9: ['8', '8'], 10: ['8', '8'], 11: ['8', '8'],
        12: ['8', '8'], 13: ['8', '8'], 14: ['8', '8'], 15: ['10', '10'],
        16: ['1', '1'], 17: ['8', '13'], 18: ['8', '13'], 19: ['14', '14'],
        20: ['14', '14'], 21: ['0', '0'], 22: ['5', '5'], 23: ['5', '5'],
        24: ['11', '11'], 25: ['18', '18'], 26: ['1', '1'], 27: ['5', '5']}

dict_banks_ZP = {0 : '21', 1 : '14', 2 : '4', 3 : '9', 5 : '11', 6 : '7',
        7 : '8', 8 : '8', 9 : '8', 10 : '8', 11 : '8', 12 : '8', 13 : '8',
        14 : '8', 15 : '6', 16 : '6', 17 : '1', 18 : '1', 19 : '1', 20 : '9',
        21 : '9', 22 : '4'}

class McemcactlTest(Test):
    def test_MCA_CTL_programmed_correctly(self):

        # Get family info
        eq_id = systeminfo.get_current_equivalent_id()

        # Get total number of cpus
        code, num_cpus, err = systeminfo.Run(["nproc"])
        for cpu in range(0, int(num_cpus)):

            # For SSP and GN
            if (eq_id in ssp_eqid or eq_id in gn_eqid):
                dict_banks = dict_banks_SSP_GN

            elif eq_id in zp_eqid:
                dict_banks = dict_banks_ZP
  
            for bank in dict_banks:
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

                # Get the mask of enable bits for each bank on each cpu
                # For SSP
                if eq_id in ssp_eqid:
                    mask_MCA_CTL = ((1 << int(dict_banks[bank][0])) - 1)

                # For GN
                elif eq_id in gn_eqid:
                    mask_MCA_CTL = ((1 << int(dict_banks[bank][1])) - 1)

                # For ZP
                elif eq_id in zp_eqid:
                    mask_MCA_CTL = ((1 << int(dict_banks[bank])) - 1)

                # If the mask of set bits is not equal to MCA_CTL register
                # value read then fail the test!
                if int(out_MCA_CTL, 16) != mask_MCA_CTL:
                    self.fail(out_MCA_CTL)

if __name__ == "__main__":
    main()
