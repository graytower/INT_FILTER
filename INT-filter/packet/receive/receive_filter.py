import socket
import parse
# import processor
import redis
import os
import time
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from scapy.all import get_if_addr
from predict import predict
# time_out=1*10 #2*20ms

Update_interval=10
Threshold=1

with open(os.path.abspath(os.path.join(os.getcwd(), ".."))+'/TIME_OUT','r') as f:
    TIME_OUT=int(f.readline())

class receive():
    def sniff(self):
        s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
        r = redis.Redis(unix_socket_path='/var/run/redis/redis.sock')       # basic database
        r2 = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=1) # pro database
        r3 = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=2) # count the number of predicted values used
        r4 = redis.Redis(unix_socket_path='/var/run/redis/redis.sock',db=3) # count the number of sending and receiving probe packets

        src_ip = get_if_addr("eth0")
        parse1 = parse.parse()
        t=[]
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
                    if r.exists(key)==True: # find this key
                        v=int(r.lindex(key,0))
                        if v<int_info[2]:
                            r.lset(key,0,int_info[2])
                            r.lset(key,1,int_info[3])
                            flag=int(r2.lindex(key,0))
                            if flag>=Update_interval:
                                # use true value                               
                                r2.linsert(key,'after',str(flag),str(int_info[2])+':'+str(int_info[3]))
                                r2.rpop(key)
                                r2.lset(key,0,0)
                                r3.incr('true')
                            else:
                                temp_l=r2.lrange(key,1,-1)
                                time_l=[]
                                value_l=[]
                                for temp in temp_l:
                                    result=temp.split(':')
                                    time_l.append(float(result[0]))
                                    value_l.append(float(result[1]))
                                time_l.reverse()    
                                value_l.reverse()
                                start=time.time()
                                pred,error,poly_order=predict(time_l,value_l,int_info[2],int_info[3])
                                # print(error)
                                if error<Threshold:
                                    # use predict value                             
                                    r2.linsert(key,'after',flag,str(int_info[2])+':'+str(pred))
                                    r2.rpop(key)
                                    num=int(r2.lindex(key,0))
                                    r2.lset(key,0,num+1)  
                                    r3.incr('predict')                                
                                else:
                                    # use true value                                  
                                    r2.linsert(key,'after',flag,str(int_info[2])+':'+str(int_info[3]))
                                    r2.rpop(key)
                                    r2.lset(key,0,0)
                                    r3.incr('true')
                                end=time.time()
                                t.append(end-start)
                    else: #not find this key
                        r.lpush(key,int_info[2],int_info[3])
            if len(t)%100==0:
                print(np.array(t).mean())

        s.close()


if __name__ == "__main__":
    receive1 = receive()
    receive1.sniff()
