import subprocess
import shlex
import sys
import random

checkIP = "dig +short myip.opendns.com @resolver1.opendns.com"
ip_addr = subprocess.check_output(checkIP, shell=True).strip().split("\n")

num_process = sys.argv[1]
index_num = random.randrange(0, 100000, 1000)
cmd = "mpiexec -n " + num_process + " python phase1_run_project.py " + str(index_num)
subprocess.Popen(shlex.split(cmd))
