import numpy as np
import os
import sys
curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(curr_dir + '/module/script')

import cvxpySolver
from observeMatrix import observeMatrix
import performanceMetric

from OpenMeasure import OpenMeasure


class TMEideal(OpenMeasure):
	def __init__(self, tmfile, sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao):
		OpenMeasure.__init__(self, tmfile, sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
		OpenMeasure.loadFile(self)
		OpenMeasure.popSNMPLinkLoad(self)
		self.swKj = {}
		self.cstr = 'SNMP + RE + ideal Top flows'

	
	def set_swKj(self, sw_Kj):
		self.swKj = sw_Kj
		Kj = sum([self.swKj[sw] for sw in self.swKj])
		self.cstr += ', K={0}'.format(Kj)


	def TMEideal(self):
		### populate OF switch routing entries
		swHj = self.OM.SDNSwitchRoutingEntries_multi()
		for sw in swHj:
			print "OF Switch {0} has routing entries {1}".format(sw, len(swHj[sw]))
	

		### construct network-wide observation matrix
		D_base = self.OM.setupOM()
		print "rank of matrix, SNMP Linkloads + Routing Entries: ", np.linalg.matrix_rank(D_base)

		### total number of TCAMs
		K = 0
		for sw in self.swKj:
			K += self.swKj[sw]
		

		t_epoch = 0
	        traffic_estm = []
        	for fl in range(self.N):
                	traffic_estm.append([])
		
        	while( t_epoch < self.Tc):			
        	        ### estimate TM
        	        col_epoch = [[row[t_epoch]] for row in self.tmTrue[0:self.N]]

			### ideally measure Top K flows without rule placement constraints
			index = sorted(range(len(col_epoch)), key = lambda k: col_epoch[k], reverse = True)
			D = D_base
			for fl in index[0:K]:
				B = np.zeros((1, self.N), dtype=np.int)
				B[0][fl] = 1
				D = np.concatenate((D,B), axis=0)
			
			""" Debug """
			print "rank of network-wide observation matrix in ideal case: ", np.linalg.matrix_rank(D)


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
