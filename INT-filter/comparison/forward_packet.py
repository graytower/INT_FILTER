# -*- coding: UTF-8 -*-
import time
import redis
from clos import gen_fattree

def forward_packet(r, spineL, leafL, torL, serverL, forward_interval=0.1):
	# 核心交换机拥有更高的处理速率。
	while True:
		for spine in spineL:
			r.decr(spine)
		for leaf in leafL:
			r.decr(leaf)
		for tor in torL:
			r.decr(tor)
		time.sleep(forward_interval/3)



if __name__ == '__main__':
	k = 2
	W = 5
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	spineL, leafL, torL, serverL = gen_fattree()
	forward_packet(r, spineL, leafL, torL, serverL)
