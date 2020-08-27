import numpy as np


def poly_predict(x_train, y_train, x_test, y_test, poly_order):
	z1 = np.polyfit(x_train, y_train, poly_order)  
	p1 = np.poly1d(z1)
	y_pred = p1(x_test)
	return y_pred,abs(y_pred-y_test)


def predict(x_train, y_train, x_test, y_test):
	pred1,error1 = poly_predict(x_train, y_train, x_test, y_test, poly_order=1)
	pred2,error2 = poly_predict(x_train, y_train, x_test, y_test, poly_order=2)
	pred3,error3 = poly_predict(x_train, y_train, x_test, y_test, poly_order=3)
	e=[error1, error2, error3]
	p=[pred1,pred2,pred3]
	m=min(e)
	ind=e.index(m)
	return p[ind],e[ind],ind+1


if __name__ == '__main__':
	
	print(predict([0, 1, 2, 3, 4], [1, 2, 1, 2, 3], 5.0, 43))
