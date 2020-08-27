# -*- coding: UTF-8 -*-
import redis


def read3(r):
	keys = r.keys()
	for key in keys:
		print(key, r.get(key))


def read2(r):
	keys = r.keys()
	for key in keys:
		print(key, r.lrange(key, 0, -1))


def read_upload_decrease(r):
	t = int(r.get('true'))
	p = int(r.get('predict'))
	return t/(t+p)


if __name__ == '__main__':
	r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)  # 存每个交换机上包的数量
	r1 = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)  # 存INT-filter历史数据
	r2 = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)  # 存INT-filter减少的上传量
	r3 = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)  # 存Sel-INT历史数据
	r4 = redis.StrictRedis(host='127.0.0.1', port=6379, db=5)  # 存Sel-INT减少的上传量
	read3(r4)
	print(read_upload_decrease(r4))
	# read2(r1)
