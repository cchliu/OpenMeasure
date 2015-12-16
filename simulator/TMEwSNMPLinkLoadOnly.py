import numpy as np
import os
import sys
curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(curr_dir + '/module/script')

import cvxpySolver
from observeMatrix import observeMatrix
import performanceMetric

from OpenMeasure import OpenMeasure


class TMEwSNMPLinkLoad(OpenMeasure):
	def __init__(self, tmfile, sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao):
		OpenMeasure.__init__(self, tmfile, sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
		OpenMeasure.loadFile(self)
		OpenMeasure.popSNMPLinkLoad(self)
		self.cstr = "SNMPLinkLoadsOnly"


	def TMEwSNMPLinkLoad(self):
		### Construct network-wide observation matrix
		D = self.OM.setupOM()

		t_epoch = 0
	        traffic_estm = []
        	for fl in range(self.N):
                	traffic_estm.append([])

        	while( t_epoch < self.Tc):
        	        ### estimate TM
        	        col_epoch = [[row[t_epoch]] for row in self.tmTrue[0:self.N]]
        	        Y = np.mat(D) * np.mat(col_epoch)
        	        Y = np.array(Y.tolist())

        	        W = np.ones([1, self.N])
        	        x_epoch = cvxpySolver.estm_TM(Y, D, W, self.N)
        	        x_epoch = [round(k) for k in x_epoch]

        	        for fl in range(self.N):
                	        traffic_estm[fl].append(x_epoch[fl])
	
        	        ### ok, we just finished one t_epoch and move to next
                	t_epoch += 1

     		""" Debug """
        	print "number of flows in tmEstm: ", len(traffic_estm)
        	print "number of time intervals in tmEstm: ", len(traffic_estm[0])
		self.tmEstm = traffic_estm

		### evaluate performance metric
		PM = performanceMetric.perfMetric(self.tmTrue, self.tmEstm, self.IPPrefix)
		return PM.calMetrics()


if __name__ == "__main__":
	pass
