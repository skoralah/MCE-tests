#!/usr/bin/env python
from avocado import Test
import subprocess
import os, re
import systeminfo
from systeminfo import Run

########################################
# Module Name = mce_sysfs_init
# Description: Check for mce sysfs device initialization
########################################

class MceTest(Test):
    @staticmethod
    def get_num_of_mc_folders():
        list_mc_folders = []
        for d in os.listdir('/sys/devices/system/machinecheck'):
            if re.match('machinecheck', d):
                list_mc_folders.append(d)
        return len(list_mc_folders)
        
    def test_MCE_sysfs_initialized(self):
        """
        Check for initialization of sysfs device for each logical CPU in the
        system
        """
        num_of_mc_folders = self.get_num_of_mc_folders()
        code, num_cpus, err = systeminfo.Run(["nproc"])
        if int(num_of_mc_folders) == int(num_cpus):
            self.log.info("MCE sysfs device initialization successful")
        else:
            self.fail("MCE sysfs device initialization failed")

if __name__ == "__main__":
    main()
