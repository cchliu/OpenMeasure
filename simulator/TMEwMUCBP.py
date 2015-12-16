import numpy as np
import os
import sys
import math
curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(curr_dir + '/module/script')

import cvxpySolver
from observeMatrix import observeMatrix
import performanceMetric

from OpenMeasure import OpenMeasure


class TMEwMUCBP(OpenMeasure):
	def __init__(self, tmfile, sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao):
		OpenMeasure.__init__(self, tmfile, sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
		OpenMeasure.loadFile(self)
		OpenMeasure.popSNMPLinkLoad(self)
		self.swKj = {}
		self.cstr = 'OpenMeasure MUCBP'

	
	def set_swKj(self, sw_Kj):
		self.swKj = sw_Kj
		Kj = sum([self.swKj[sw] for sw in self.swKj])
		self.cstr += ', K={0}'.format(Kj)


	def set_windowSize(self, windowSize):
		self.windowSize = windowSize


	def set_rulePlacementAlgo(self, algo):
		self.method = algo
		self.cstr += ', {0}'.format(algo)
 

	def TMEwMUCBP(self):
                traffic_estm = []
                for fl in range(self.N):
                        traffic_estm.append([])

		### populate OF switch routing entries
		swHj = self.OM.SDNSwitchRoutingEntries_multi()
		for sw in swHj:
			print "OF Switch {0} has routing entries {1}".format(sw, len(swHj[sw]))
	
		### static aggregation: MLRF
		swHj = self.OM.MLRF_multi(self.swKj)
		for sw in swHj:
			print "OF Switch {0} has entries (RE+ME) {1}".format(sw, len(swHj[sw]))		

		### construct network-wide observation matrix
		D = self.OM.setupOM()
		
		t_epoch = 0
		### MLRF to boot-strap online learning algorithms
		col_epoch = [[row[t_epoch]] for row in self.tmTrue[0:self.N]]
		Y = np.mat(D) * np.mat(col_epoch)
		Y = np.array(Y.tolist())
		
		W = np.ones([1, self.N])
		x_epoch = cvxpySolver.estm_TM(Y, D, W, self.N)
		x_epoch = [round(k) for k in x_epoch]
		
		for fl in range(self.N):
			traffic_estm[fl].append(x_epoch[fl])

		if(self.windowSize == 0):
			self.windowSize = self.Tc
		""" Debug """
		print "static window size is: ", self.windowSize

		### MUCBP online learning algorithm
		alpha = 0.1
		xj = []
		tj = []
		Ij = []
		tc = 0
		
		# initialize xj
                t_epoch = 0
                xj = [row[t_epoch] for row in traffic_estm]
                tj = [1 for row in self.tmTrue]
                Ij = [0 for row in self.tmTrue]
                tc = self.N
                t_epoch += 1

		# update xj, even flow fl is not directly measured	
		count = 1
        	while( t_epoch < self.Tc):
			
			# MUCB Prediction
			for k in range(self.N):
				Ij[k] = alpha * xj[k] + math.sqrt(2.0 * math.log(tc) / float(tj[k]))
			index = sorted(range(len(Ij)), key = lambda k:Ij[k], reverse=True)

			# rule placement
			if self.method == "LastHop": 
				[sw_bj, D] = self.OM.LastHop(index, self.swKj, False)
			elif self.method == "Greedy":
				[sw_bj, D] = self.OM.Greedy(index, self.swKj, False)
			elif self.method == "ILP":
				[sw_bj, D] = self.OM.ILP(Ij, self.swKj)
				

        	        ### estimate TM
        	        col_epoch = [[row[t_epoch]] for row in self.tmTrue[0:self.N]]
        	        Y = np.mat(D) * np.mat(col_epoch)
        	        Y = np.array(Y.tolist())

        	        W = np.ones([1, self.N])
        	        x_epoch = cvxpySolver.estm_TM(Y, D, W, self.N)
        	        x_epoch = [round(k) for k in x_epoch]

        	        for fl in range(self.N):
                	        traffic_estm[fl].append(x_epoch[fl])
	
			# update tj
			for sw in sw_bj:
				for fl in sw_bj[sw]:
					tj[fl] += 1
			# update xj
			#for sw in sw_bj:
			#	for fl in sw_bj[sw]:
			#		xj[fl] = (xj[fl] * (tj[fl]-1) + x_epoch[fl]) / float(tj[fl])
			
			# update xj: version 2
			for fl in range(self.N):
				xj[fl] = ((xj[fl] * count) + x_epoch[fl]) / float(count + 1)

			# update tc
			tc += sum([self.swKj[sw] for sw in self.swKj])

			if(t_epoch % self.windowSize == 0):
				tj = [1 for k in tj]
				tc = self.N
				count = 1

        	        ### ok, we just finished one t_epoch and move to next
                	t_epoch += 1
			count += 1

     		""" Debug """
        	print "number of flows in tmEstm: ", len(traffic_estm)
        	print "number of time intervals in tmEstm: ", len(traffic_estm[0])
		self.tmEstm = traffic_estm

		### evaluate performance metric
		PM = performanceMetric.perfMetric(self.tmTrue, self.tmEstm, self.IPPrefix)
		return PM.calMetrics()


if __name__ == "__main__":
	pass
