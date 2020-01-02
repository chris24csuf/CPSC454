from mpi4py import MPI
from time import time as timer
import subprocess
import sys

def output_rnd(proc_num, ip_address, start_time):
    end = timer()
    print "\n\nprocess", proc_num, "at", ip_address, "found the random index in {:0.2f} second(s)".format(end-start_time)

def output_last(proc_num, ip_address, start_time):
    end = timer()
    print "process", proc_num, "at", ip_address, "found the last index in {:0.2f} second(s)".format(end-start_time)

start = timer()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

index_size = 100000
list = [0]*index_size
list[int(sys.argv[1])] = 1      # expected runtime
list[index_size-1] = 2          # worse-case runtime

checkIP = "dig +short myip.opendns.com @resolver1.opendns.com"
ip_addr = subprocess.check_output(checkIP, shell=True).strip().split("\n")

# first segment
if rank == 0:
    index_range = (index_size/size)
    for x in list[0:index_range]:
        for y in list[0:index_range]:
            if x > 0 and x == y and x == 1:
                output_rnd(rank, ip_addr[0], start)
            if x > 0 and x == y and x == 2:
                output_last(rank, ip_addr[0], start)

# last segment
elif rank == size-1:
    index_range = (index_size/size)*(size-1)
    for x in list[index_range:index_size]:
        for y in list[index_range:index_size]:
            if x > 0 and x == y and x == 1:
                output_rnd(rank, ip_addr[0], start)
            if x > 0 and x == y and x == 2:
                output_last(rank, ip_addr[0], start)

# in-between segments
else:
    start_index_range = (index_size/size)*rank
    stop_index_range = (index_size/size)*(rank+1)
    for x in list[start_index_range:stop_index_range]:
        for y in list[start_index_range:stop_index_range]:
            if x > 0 and x == y and x == 1:
                output_rnd(rank, ip_addr[0], start)
            if x > 0 and x == y and x == 2:
                output_last(rank, ip_addr[0], start)
