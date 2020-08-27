# -*- coding: UTF-8 -*-
import redis
import subprocess
import time
import numpy as np
from read_redis import read3


def database_init(r, r1, r2,r3,r4, spineL, leafL, torL):
	r.flushall()
	r2.set('true', 0)
	r2.set('predict', 0)
	r4.set('true', 0)
	r4.set('predict', 0)

	for s in spineL + leafL + torL:
		r.set(s, 0)
		r1.lpush(s, 0)
		r3.lpush(s,0)
		r3.lpush(s,'-1')
		for i in range(W):
			r1.rpush(s, '-1')

def read_INTfilter_upload_decrease(r):
	t = int(r.get('true'))
	p = int(r.get('predict'))
	return 26*1.0*p/(32*(t+p))

def read_SelINT_upload_decrease(r):
	t = int(r.get('true'))
	p = int(r.get('predict'))
	return t/(t+p)

def gen_fattree(k=20):
	spineL = [(i + 1) * 10 - 1 for i in range(k)] + [(i + 1) * 10 for i in range(k)]
	leafL = [(i + 1) * 10 - 2 for i in range(k)] + [(i + 1) * 10 - 3 for i in range(k)]
	torL = [(i + 1) * 10 - 4 for i in range(k)] + [(i + 1) * 10 - 5 for i in range(k)]
	serverL = [i * 10 + 1 for i in range(k)] + [i * 10 + 2 for i in range(k)] + [i * 10 + 3 for i in range(k)] + [
		i * 10 + 4 for i in range(k)]
	return spineL, leafL, torL, serverL

def calculate_absolute_error(r1):
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	true = []
	predict = []
	keys = r.keys()
	for key in keys:
		true.append(float(r.get(key)))
		predict.append(float(r3.lrange(key, 1, -1)[0]))
	return np.sum(np.abs(np.array(true) - np.array(predict)))

def calculate_relative_error(r1):
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	true=[]
	predict=[]
	keys=r.keys()
	for key in keys:
		true.append(float(r.get(key)))
		predict.append(float(r3.lrange(key, 1, -1)[0]))
	error=np.sum(np.abs(np.array(true)-np.array(predict)))
	return error/np.sum(np.array(true))

if __name__ == '__main__':
	W = 5
	spineL, leafL, torL, serverL = gen_fattree()
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	r1 = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)  # 存INT-filter历史数据
	r2 = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)  # 存INT-filter减少的上传量
	r3 = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)  # 存Sel-INT历史数据
	r4 = redis.StrictRedis(host='127.0.0.1', port=6379, db=5)  # 存Sel-INT减少的上传量
	database_init(r, r1, r2,r3,r4, spineL, leafL, torL)
	p1 = subprocess.Popen('python ./send_int.py', shell=True)
	p2 = subprocess.Popen('python ./send_traffic.py', shell=True)
	p3 = subprocess.Popen('python ./forward_packet.py', shell=True)
	p4 = subprocess.Popen('python ./INT-filter.py', shell=True)
	p5=subprocess.Popen('python ./Sel-INT.py', shell=True)

	start = time.time()
	while time.time() - start < 10:
		time.sleep(1)
		print('INT-filter decrease:',read_INTfilter_upload_decrease(r2))
		print('Sel-INT decrease:',read_SelINT_upload_decrease(r4))
		# print('INT-filter abs error:', calculate_absolute_error(r1))
		# print('Sel-INT abs error:',calculate_absolute_error(r3))
		# print('INT-filter relative error:', calculate_relative_error(r1))
		# print('Sel-INT relative error:', calculate_relative_error(r3))
		print('')

	# 杀死所有进程和后台exe
	p1.kill()
	p2.kill()
	p3.kill()
	p4.kill()
	p5.kill()
	kill_command = 'taskkill /f /im python.exe /t'
	cc = subprocess.Popen(kill_command, shell=True)
