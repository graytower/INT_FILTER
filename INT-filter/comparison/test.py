# -*- coding: UTF-8 -*-
import numpy as np

if __name__=='__main__':
	l=2
	print(np.mean(np.random.poisson(lam=l,size=1000)))