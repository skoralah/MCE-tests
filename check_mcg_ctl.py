#!/usr/bin/env python
from avocado import Test
import subprocess
from subprocess import Popen, PIPE
import os, re
import systeminfo
from systeminfo import *

MCG_CTL_MASK = 0xffffffffffffffff
MASTER_TH_MASK = 0xffffffffffffffef #For SSP and GN
NON_MASTER_TH_MASK = 0x6f           #For SSP and GN
ZP_MASK = 0xffffffffffffffef

########################################
# Module Name: check_mcg_ctl
# Description: This module tests if MCG_CTL is programmed correctly for all
#              logical CPUs for families ZP, SSP and GN
########################################

class MceTest(Test):
    def test_MCG_CTL_programmed_correctly(self):
        dict_MCG_CTL = {}
        dict_MCG_CTL_mask = {}
        list_master_threads = []
        cpu_topo = []

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

        # Get total number of logical CPUs and read MCG_CTL and MCG_CAP
        # across all CPUs
        code, num_cpus, err = systeminfo.Run(["nproc"])
        for cpu in range(0, int(num_cpus)):
            code, out_MCG_CTL, err = systeminfo.Run(["rdmsr -p %s 0x017b" % (cpu)])
            code, out_MCG_CAP, err = systeminfo.Run(["rdmsr -p %s 0x0179" % (cpu)])

            # Remove new lines
            out_MCG_CTL = out_MCG_CTL.strip('\n')
            out_MCG_CAP = out_MCG_CAP.strip('\n')

            # Get MCG_CAP[Count] value, Bits[0:7] of MCG_CAP
            out_MCG_CAP_count = int(out_MCG_CAP, 16) & int(0xff)

            # Create a mask of set bits for MCG_CAP[Count]
            mask_MCG_CAP_count = ((1 << (out_MCG_CAP_count)) - 1)
            dict_MCG_CTL.update( {cpu : out_MCG_CTL} )
            dict_MCG_CTL_mask.update( {cpu : mask_MCG_CAP_count} )

        # Get number of threads, sockets and cores
        cpu_info = systeminfo.get_cpu_info()
        for elem in cpu_info:
            elem = elem.split(':')[-1]
            cpu_topo.append(elem)

        # For SSP and GN
        if (int(family, 16) == int("0x17", 16) and int(model, 16) in \
                range(0x30, 0x3f)) or (int(family, 16) == int("0x19", 16) \
                and int(model, 16) in range (0x00, 0x0f)):

            # Extract MCA master threads on all cores/sockets
            # cpu_topo[0] = Thread(s) per core
            # cpu_topo[1] = Core(s) per socket
            # cpu_topo[2] = Socket(s)
            for i in range(0, int(cpu_topo[1])*int(cpu_topo[2]),
                    int(cpu_topo[1])):

                # For Master threads
                for cpu in range(0, 8):
                    if int(dict_MCG_CTL[cpu+i], 16) & \
                            int(dict_MCG_CTL_mask[cpu+i]) == \
                            int(dict_MCG_CTL_mask[cpu+i]) or \
                            int(dict_MCG_CTL[cpu+i], 16) & \
                            int(MASTER_TH_MASK) == int(MASTER_TH_MASK):
                        list_master_threads.append(cpu+i)
                    else:
                        self.fail("MCG_CTL not programmed correctly for CPU%d", cpu+i)

            # For Non-Master threads
            for cpu in range(0, int(num_cpus)):
                # Exclude Master threads
                if cpu not in list_master_threads:
                    if int(dict_MCG_CTL[cpu], 16) & \
                            int(dict_MCG_CTL_mask[cpu]) != \
                            int(dict_MCG_CTL_mask[cpu]) and \
                            int(dict_MCG_CTL[cpu], 16) & \
                            int(NON_MASTER_TH_MASK) != int(NON_MASTER_TH_MASK):
                        self.fail("MCG_CTL not programmed correctly for CPU%d", cpu)

        # For ZP
        elif int(family, 16) == int("0x17", 16) and int(model, 16) \
                in range(0x00, 0x0f):
            for cpu in range(0, int(num_cpus)):
                if int(dict_MCG_CTL[cpu], 16) & \
                        int(dict_MCG_CTL_mask[cpu]) != \
                        int(dict_MCG_CTL_mask[cpu]) and \
                        int(dict_MCG_CTL[cpu], 16) & \
                        int(ZP_MASK) != int(ZP_MASK):
                    self.fail("MCG_CTL not programmed correctly for CPU%d", cpu)

if __name__ == "__main__":
    main()
