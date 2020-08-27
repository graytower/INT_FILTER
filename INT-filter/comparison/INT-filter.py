import redis
import os
import time
import numpy as np
from predict import predict
import random
from clos import gen_fattree

# time_out=1*10 #2*20ms

Update_interval = 10
Threshold = 1


def gen_int_path(spineL, leafL, torL, serverL):
	pathL = []
	spineNum = len(spineL)
	server_pair = list(np.array(serverL).reshape((-1, 2)))
	for pair in server_pair:
		path = []
		start = pair[0]
		end = pair[1]
		t1 = int(start / 10)
		t2 = int(end / 10)
		if start % 10 == 1 or start % 10 == 2:
			path.append(t1 * 10 + 5)
		else:
			path.append(t1 * 10 + 6)
		path.append(random.choice([t1 * 10 + 7, t1 * 10 + 8]))
		if path[-1] % 10 == 7:
			path.append(random.choice(spineL[:int(spineNum / 2)]))
		else:
			path.append(random.choice(spineL[int(spineNum / 2):]))
		if path[-1] %10==9:
			path.append(t2*10+7)
		else:
			path.append(t2*10+8)
		if end % 10 == 1 or end % 10 == 2:
			path.append(t2 * 10 + 5)
		else:
			path.append(t2 * 10 + 6)
		pathL.append(path)
	return pathL


def filter(W=5):
	spineL, leafL, torL, serverL = gen_fattree()
	pathL = gen_int_path(spineL, leafL, torL, serverL)

	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	r1 = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)  # 存历史数据
	r2 = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)  # 存INT-filter减少的上传量

	t = []
	true = []
	pre = []
	while True:
		for path in pathL:
			for s in path:
				flag = int(r1.lindex(s, 0))
				if flag >= Update_interval:
					# use true value
					q=float(r.get(s))
					r1.linsert(s, 'after', flag, q)
					r1.rpop(s)
					r1.lset(s, 0, 0)
					true.append(q)
					pre.append(q)
					r2.incr('true')
				else:
					temp_l = r1.lrange(s, 1, -1)
					temp_l.reverse()
					value_l=[float(q) for q in temp_l]
					time_l = np.arange(0,W,1)
					start = time.time()
					q=float(r.get(s))
					pred, error, poly_order = predict(time_l, value_l, W, q)
					# print(error)
					if error < Threshold:
						# use predict value
						r1.linsert(s, 'after', flag, float(pred))
						r1.rpop(s)
						num = int(r1.lindex(s, 0))
						r1.lset(s, 0, num + 1)
						true.append(q)
						pre.append(float(pred))
						r2.incr('predict')
					else:
						# use true value
						r1.linsert(s, 'after', flag, q)
						r1.rpop(s)
						r1.lset(s, 0, 0)
						true.append(q)
						pre.append(q)
						r2.incr('true')
					end = time.time()
					t.append(end - start)
		time.sleep(0.1)
		if len(true)%100==0:
			print('INT-filter error:',np.sum(np.abs(np.array(true)[-100:] - np.array(pre)[-100:]))/100)
		# if len(t) % 100 == 0:
		# 	print('INT-filter time:',np.array(t).mean())

if __name__ == "__main__":
	filter()
