# -*- coding: UTF-8 -*-
import time
import redis
import numpy as np
from clos import gen_fattree

def send_traffic(r, spineL, leafL, torL, serverL, send_traffic_interval=0.1):
	# 发送背景流，越核心数据量越大，每秒以随机数量上涨
	l = 2
	while True:
		for spine in spineL:
			r.set(spine, int(r.get(spine)) + np.random.poisson(lam=l))
		for leaf in leafL:
			r.set(leaf, int(r.get(leaf)) + np.random.poisson(lam=l))
		for tor in torL:
			r.set(tor, int(r.get(tor)) + np.random.poisson(lam=l))
		time.sleep(send_traffic_interval)




if __name__ == '__main__':
	k = 2
	W = 5
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	spineL, leafL, torL, serverL = gen_fattree()
	send_traffic(r, spineL, leafL, torL, serverL)
