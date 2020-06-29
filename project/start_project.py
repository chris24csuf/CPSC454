from multiprocessing.managers import BaseManager
import multiprocessing
import subprocess
import threading
import random
import socket
import shlex
import time
import sys

def mpi_proc(rnd_index):
    cmd = "mpiexec -n " + num_process + " python /home/cpsc454/run_project.py " + str(rnd_index)
    subprocess.Popen(shlex.split(cmd))

class listening_thread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.settimeout(2)
        while LISTEN_LOOP:
            try:
                sock.listen(5)
                conn, addr = sock.accept()
                conn_thread = connection_thread(conn, addr)
                conn_thread.start()
                print 'connection thread started for', addr[0]
            except:
                pass

class connection_thread(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.daemon = True
        self.conn = conn
        self.addr = addr

    def run(self):
        while True:
            data = self.conn.recv(1024)
            msg = data.decode('ascii')
            if msg.strip() == 'start':
                random_index_location = random.randrange(0, 1000000, 10)
                mpi_process = multiprocessing.Process(target=mpi_proc, args=(random_index_location,))
                mpi_process.daemon = True
                mpi_process.start()
                print 'started simulation for', self.addr[0]
                msg_response = None
                while True:
                    if not message.empty():
                        msg_receive = message.get()
                        if msg_receive[0] == str(random_index_location):
                            msg_response = str(msg_receive[1]) + ' ' + str(msg_receive[2])
                            break
                        else:
                            message.put(msg_receive)
                            time.sleep(0.25)
                self.conn.send(msg_response.encode('ascii'))
                mpi_process.join()
                print 'simulation for', self.addr[0], 'complete'
                break
        self.conn.close()
        print 'connection to', self.addr[0], 'closed'

print '\033c'
checkIP = "dig +short myip.opendns.com @resolver1.opendns.com"
ip_addr = subprocess.check_output(checkIP, shell=True).strip().split("\n")
num_process = sys.argv[1]
print 'Main process at master node with ip address', ip_addr[0]

msg_queue = multiprocessing.Queue()
BaseManager.register('msg', callable=lambda: msg_queue)
manager = BaseManager(address=('', 54322), authkey=b'dc2s')
manager.start()
message = manager.msg()
print 'create message queue manager at port 54322 complete'

LISTEN_LOOP = True
listen = listening_thread('', 54321)
listen.start()
print 'create listening thread at port 54321 complete'

input = raw_input()
LISTEN_LOOP = False
listen.join()
manager.shutdown()
msg_queue.close()
print 'Shutdown complete'
