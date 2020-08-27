# -*- coding: UTF-8 -*-
import time
import redis
from clos import gen_fattree

def send_int(r, spineL, leafL, torL, serverL, send_int_interval=0.1):
	# 发送INT包，就定时给所有交换机+1
	while True:
		for s in spineL + leafL + torL:
			r.incr(str(s))
		time.sleep(send_int_interval)



if __name__ == '__main__':
	W = 5
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	spineL, leafL, torL, serverL = gen_fattree()
	send_int(r, spineL, leafL, torL, serverL)
