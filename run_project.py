from multiprocessing.managers import BaseManager
from time import time as timer
from mpi4py import MPI
import multiprocessing
import subprocess
import threading
import sys

class data_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        for process in range(size):
            if process > 0 and process < size-1:
                start_index_range = (index_size/size)*process
                stop_index_range = (index_size/size)*(process+1)
                data = main_list[start_index_range:stop_index_range]
                comm.send(data, dest=process, tag=process)
            elif process == size-1:
                index_range = (index_size/size)*(size-1)
                data = main_list[index_range:index_size]
                comm.send(data, dest=process, tag=process)

class segment_thread(threading.Thread):
    def __init__(self, list):
        threading.Thread.__init__(self)
        self.daemon = True
        self.list = list

    def run(self):
        for x in self.list:
            for y in self.list:
                if x > 0 and x == y and x == 1:
                    output_rnd(rank, ip_addr[0], start)
                if x > 0 and x == y and x == 2:
                    output_last(rank, ip_addr[0], start)

class manager_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        BaseManager.register('msg')
        manager = BaseManager(address=('localhost', 54322), authkey=b'dc2s')
        manager.connect()
        msg_manager = manager.msg()

        msg_list = []
        msg_list.append(str(sys.argv[1]))
        rnd_msg = comm.recv(source=MPI.ANY_SOURCE, tag=0)
        msg_list.append(rnd_msg)
        last_msg = comm.recv(source=MPI.ANY_SOURCE, tag=1)
        msg_list.append(last_msg)
        msg_manager.put(msg_list)

def output_rnd(proc_num, ip_address, start_time):
    end = timer()
    msg = '{:0.2f}'.format(end-start_time)
    print "process", proc_num, "at", ip_address, "found the random index in {:0.2f} second(s)".format(end-start_time)
    comm.send(msg, dest=0, tag=0)

def output_last(proc_num, ip_address, start_time):
    end = timer()
    msg = '{:0.2f}'.format(end-start_time)
    print "process", proc_num, "at", ip_address, "found the last index in {:0.2f} second(s)".format(end-start_time)
    comm.send(msg, dest=0, tag=1)

start = timer()
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

checkIP = "dig +short myip.opendns.com @resolver1.opendns.com"
ip_addr = subprocess.check_output(checkIP, shell=True).strip().split("\n")
segment_range = 25

# first segment
if rank == 0:
    index_size = 1000000
    main_list = [0]*index_size
    main_list[int(sys.argv[1])] = 1      # expected runtime
    main_list[index_size-1] = 2          # worse-case runtime

    message_manager = manager_thread()
    message_manager.start()

    index_range = (index_size/size)
    list = main_list[0:index_range]
    list_size = len(list)
    segment_list = []
    start_list = 0
    end_list = segment_range
    list_offset = list_size-end_list

    if list_size < segment_range:
        start_list = 0
        end_list = list_size
        for x in list[start_list:end_list]:
            for y in list[start_list:end_list]:
                if x > 0 and x == y and x == 1:
                    output_rnd(rank, ip_addr[0], start)
                if x > 0 and x == y and x == 2:
                    output_last(rank, ip_addr[0], start)
    else:
        split_data = data_thread()
        split_data.start()

        segment = segment_thread(list[start_list:end_list])
        segment.start()
        segment_list.append(segment)

        while end_list < list_size:
            if list_offset < segment_range:
                start_list += segment_range
                end_list += list_offset
                segment = segment_thread(list[start_list:end_list])
                segment.start()
                segment_list.append(segment)
            else:
                start_list += segment_range
                end_list += segment_range
                segment = segment_thread(list[start_list:end_list])
                segment.start()
                segment_list.append(segment)

        for segment in segment_list:
            segment.join()
        split_data.join()
    message_manager.join()

# other segments
else:
    list = comm.recv(source=0, tag=rank)
    list_size = len(list)
    segment_list = []
    start_list = 0
    end_list = segment_range
    list_offset = list_size-end_list

    if list_size < segment_range:
        start_list = 0
        end_list = list_size
        for x in list[start_list:end_list]:
            for y in list[start_list:end_list]:
                if x > 0 and x == y and x == 1:
                    output_rnd(rank, ip_addr[0], start)
                if x > 0 and x == y and x == 2:
                    output_last(rank, ip_addr[0], start)
    else:
        while end_list < list_size:
            if list_offset < segment_range:
                start_list += segment_range
                end_list += list_offset
                segment = segment_thread(list[start_list:end_list])
                segment.start()
                segment_list.append(segment)
            else:
                start_list += segment_range
                end_list += segment_range
                segment = segment_thread(list[start_list:end_list])
                segment.start()
                segment_list.append(segment)

        start_list = 0
        end_list = segment_range
        for x in list[start_list:end_list]:
            for y in list[start_list:end_list]:
                if x > 0 and x == y and x == 1:
                    output_rnd(rank, ip_addr[0], start)
                if x > 0 and x == y and x == 2:
                    output_last(rank, ip_addr[0], start)

        for segment in segment_list:
            segment.join()
