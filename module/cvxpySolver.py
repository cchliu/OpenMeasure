""" CVXPY SOLVER FOR ESTIMATE TM """

import numpy as np
from cvxpy import *
import math


### minimize sum_sqaures(Y - D*X) + lambda * (W * X)
def estm_TM(Y, D, W, N):
	X = Variable(N, 1)
	
	obj = Minimize(sum_squares(Y-D*X) + 0.01*(W*X))
	constraints = [0 <= X]
	
	prob = Problem(obj, constraints)
	prob.solve()
	x_epoch = [X.value[i][0,0] for i in range(N)]
	return x_epoch


if __name__ == "__main__":
	pass
	
