import redis
import os
import time
import numpy as np
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
		if path[-1] % 10 == 9:
			path.append(t2 * 10 + 7)
		else:
			path.append(t2 * 10 + 8)
		if end % 10 == 1 or end % 10 == 2:
			path.append(t2 * 10 + 5)
		else:
			path.append(t2 * 10 + 6)
		pathL.append(path)
	return pathL


def filter(W=1):
	spineL, leafL, torL, serverL = gen_fattree()
	pathL = gen_int_path(spineL, leafL, torL, serverL)

	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	r3 = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)  # 存Sel-INT历史数据
	r4 = redis.StrictRedis(host='127.0.0.1', port=6379, db=5)  # 存Sel-INT减少的上传量

	t = []
	true = []
	pre = []
	while True:
		for path in pathL:
			for s in path:
				flag = int(r3.lindex(s, 0))
				if flag >= Update_interval:
					# use true value
					q = float(r.get(s))
					r3.linsert(s, 'after', flag, q)
					r3.rpop(s)
					r3.lset(s, 0, 0)
					true.append(q)
					pre.append(q)
					r4.incr('true')
				else:
					temp_l = r3.lrange(s, 1, -1)
					data_p = float(temp_l[0])
					data = float(r.get(s))
					flag = abs(data_p - data) / min(data_p, data, -0.0000001)
					start = time.time()
					# print(error)
					if flag > Threshold:
						# use true value
						r3.linsert(s, 'after', flag, data)
						r3.rpop(s)
						r3.lset(s, 0, 0)
						true.append(data)
						pre.append(data)
						r4.incr('true')
					else:
						# use predict value
						num = int(r3.lindex(s, 0))
						r3.lset(s, 0, num + 1)
						true.append(data)
						pre.append(data_p)
						r4.incr('predict')
					end = time.time()
					t.append(end - start)
		time.sleep(0.1)
		if len(true) % 100 == 0:
			print('Sel-INT error:', np.sum(np.abs(np.array(true)[-100:] - np.array(pre)[-100:])) / 100)

		# if len(t) % 100 == 0:
		# 	print('Sel-INT time:',np.array(t).mean())


if __name__ == "__main__":
	filter()
