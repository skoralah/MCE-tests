import subprocess
from subprocess import call, Popen, PIPE

def Run(cmd):
    """
    Run a cmd[], return the exit code, stdout, and stderr.
    """
    proc=subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True, universal_newlines=True)
    out, err = proc.communicate()
    return proc.returncode, out, err

def get_current_equivalent_id():
    """
    Returns the current equivalent_id in reg eax at function 0x80000001 in
    cpuid
    """
    cpuid_info = Popen(["cpuid", "-1", "-r"], stdout=PIPE,
            universal_newlines=True)
    cpuid = Popen(["grep", "0x80000001"], stdin=cpuid_info.stdout,
            stdout=PIPE, universal_newlines=True).communicate()[0]
    cpuid_info.stdout.close()
    cpu_id = cpuid.split(" ")
    eq_id = cpu_id[5][4:14]
    return eq_id

def get_cpu_info():
    """
    Returns Number of thread(s) per core, number of core(s) per socket
    and number of socket(s)
    """
    lscpu_info = Popen(["lscpu"], stdout=PIPE, universal_newlines=True)
    cpu_info = Popen(["grep", "-E", "'|^Thread|^Core|^Socket|\('"],
            stdin=lscpu_info.stdout, stdout=PIPE,
            universal_newlines=True).communicate()[0]
    lscpu_info.stdout.close()
    cpu_info = cpu_info.strip('\n').split('\n')
    return cpu_info

def get_family_info():
    """
    Returns Number of thread(s) per core, number of core(s) per socket
    and number of socket(s)
    """
    lscpu_info = Popen(["lscpu"], stdout=PIPE, universal_newlines=True)
    family = Popen(["grep", "CPU family"],
            stdin=lscpu_info.stdout, stdout=PIPE,
            universal_newlines=True).communicate()[0]
    lscpu_info.stdout.close()
    return family

if __name__ ==  "__main__":
    main()
