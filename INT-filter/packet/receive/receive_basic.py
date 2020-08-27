import socket
import parse
# import processor
import redis
import os
import time

from scapy.all import get_if_addr
# time_out=1*10 #2*20ms
with open(os.path.abspath(os.path.join(os.getcwd(), ".."))+'/TIME_OUT','r') as f:
    TIME_OUT=int(f.readline())

class receive():
    def sniff(self):
        s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
        r = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=0)       # basic database
        # r2 = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=1) # persist database
        r4 = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=3) # data database
        src_ip = get_if_addr("eth0")
        parse1 = parse.parse()
        while True:
            data = s.recv(2048)
            if not data:
                print ("Client has exist")
                continue         
            
            rs = parse1.filter(data)    # None: data packet without int info; False: not data packet
            # rs= dip,dmac,port1,port2,port3,delta_time
            if rs != None:
                if rs != False:
                    r4.incr('receive')
                    # continue
                else:
                    continue
                for int_info in rs:
                    # print(int_info)
                    key=str(int_info[0])+'-'+str(int_info[1])
                    # value=[int_info[2],int_info[3]]
                    start=time.time()
                    if r.exists(key)==True: # find this key
                        v=int(r.lindex(key,0))
                        if v<int_info[2]:
                            r.lset(key,0,int_info[2])
                            r.lset(key,1,int_info[3])
                    else: #not find this key
                        r.lpush(key,int_info[2],int_info[3])
                    end=time.time()
                    # print(end-start)

        s.close()


if __name__ == "__main__":
    receive1 = receive()
    receive1.sniff()
