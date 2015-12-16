""" Performance Metric """

import numpy as np
import math
import tree

class perfMetric(object):
	def __init__(self,tm_true, tm_estm, IPPrefix, theta=0.05):
		self.tmTrue = tm_true
		self.tmEstm = tm_estm
		# number of time intervals
		self.Tc = len(self.tmTrue[0])
		# number of flows
		self.N = len(self.tmTrue)

		# calculate maximum flow size in dataset
                self.maxSize = 0
                for i in range(self.N):
                        for j in range(self.Tc):
                                if self.maxSize < self.tmTrue[i][j]:
                                        self.maxSize = self.tmTrue[i][j]
                print "maximum flow size in dataset: ", self.maxSize

		# IP prefiex
		self.IPPrefix = IPPrefix
	
		# user-defined threashold
		self.theta = theta

		# create Hierarchical tree
		self.HTreeTrue = tree.HTree()
		self.HTreeTrue.create(self.HTreeTrue.head)
		self.HTreeEstm = tree.HTree()
		self.HTreeEstm.create(self.HTreeEstm.head)

 	
	### calculate NMSE
	def calNMSE(self):
		aveNMSE = 0
		for t_epoch in range(self.Tc):
			error = [self.tmTrue[i][t_epoch] - self.tmEstm[i][t_epoch] for i in range(self.N)]
			col_true = [self.tmTrue[i][t_epoch] for i in range(self.N)]

			MSE = np.linalg.norm(error, ord=2)
			MSE_d = np.linalg.norm(col_true, ord=2)
		
			NMSE = MSE / MSE_d
			aveNMSE += NMSE
		return aveNMSE / float(self.Tc)  
	

	### calculate HHI
	def calHHI(self):
		num_HH = 0
    		Pd_HH_ave = 0
    		Pfa_HH_ave = 0
    		for t_epoch in range(self.Tc):
			col_true = [self.tmTrue[fl][t_epoch] for fl in range(self.N)]
			col_estm = [self.tmEstm[fl][t_epoch] for fl in range(self.N)]
			HH_true = [fl for fl in range(self.N) if col_true[fl] >= self.theta*self.maxSize]
			HH_estm = [fl for fl in range(self.N) if col_estm[fl] >= self.theta*self.maxSize]			

			HHI = [fl for fl in HH_estm if fl in HH_true]
			Pd_HH = len(HHI) / float(len(HH_true))

			Pfa_HH = (len(HH_estm)-len(HHI)) / float(self.N - len(HH_true))
			Pd_HH_ave += Pd_HH
			Pfa_HH_ave += Pfa_HH
			num_HH += len(HH_true)

    		Pd_HH_ave = Pd_HH_ave / float(self.Tc)
    		Pfa_HH_ave = Pfa_HH_ave / float(self.Tc)
    		num_HH_ave = num_HH / float(self.Tc)
    		return [Pd_HH_ave, Pfa_HH_ave, num_HH_ave]

	
	### find HHH node
	def update_HHH_val(self, node):
		if node == None:
			return 0
		HHHVal_left = self.update_HHH_val(node.left)
		HHHVal_right = self.update_HHH_val(node.right)
		tmp = node.getVal() - HHHVal_left - HHHVal_right
		if tmp >= self.theta*self.maxSize:
			node.setIsHHH(1)
			node.setHHHVal(node.getVal())
			return node.getHHHVal()
		else:
			node.setHHHVal(HHHVal_left + HHHVal_right)
			return node.getHHHVal()

			  	
	### store all HHH nodes in a list
	def store_HHH_node(self, node, HHHList):
		if node == None:
			return
		if node.isHHH == 1:
			HHHList.append(node.getNodeID())
		self.store_HHH_node(node.left, HHHList)
		self.store_HHH_node(node.right, HHHList)


	# calculate HHHI
	def calHHHI(self):
		precision_ave = 0
		recall_ave = 0
		num_HHH = 0

		# number of IPs
		numIPs = len(self.IPPrefix)
		for t_epoch in range(self.Tc):
			col_true = [row[t_epoch] for row in self.tmTrue]
			col_estm = [row[t_epoch] for row in self.tmEstm]	
		
			HHH_d = 0
			numHHH_true = 0
			numHHH_estm = 0
			
			for dstIP in range(numIPs):
				# clear tree
				self.HTreeTrue.clear(self.HTreeTrue.head)
				self.HTreeEstm.clear(self.HTreeEstm.head)

				# fill hierarchical tree
				for srcIP in range(numIPs):	
					prefix = bin(self.IPPrefix[srcIP][0])[2:]
					prefix = (self.HTreeTrue.bitLenth-len(prefix))* '0' + prefix
					prefix = [int(k) for k in list(prefix)]
					#print prefix
					flNum = dstIP * numIPs + srcIP
					self.HTreeTrue.fill(prefix, col_true[flNum])
					self.HTreeEstm.fill(prefix, col_estm[flNum])
				
				# find HHH node	
				self.update_HHH_val(self.HTreeTrue.head)
				self.update_HHH_val(self.HTreeEstm.head)

				""" Debug """
				#self.HTreeTrue.plot(self.HTreeTrue.head)
				#print "maxsize in dataset: ", self.maxSize
	
				# get HHH node list
				HHHList_true = []
				HHHList_estm = []
				self.store_HHH_node(self.HTreeTrue.head, HHHList_true)
				self.store_HHH_node(self.HTreeEstm.head, HHHList_estm)
			
				HHH_d += len([k for k in HHHList_estm if k in HHHList_true])
				numHHH_true += len(HHHList_true)
				numHHH_estm += len(HHHList_estm)
			precision_ave += HHH_d / float(numHHH_true)
			recall_ave += HHH_d / float(numHHH_estm)
			num_HHH += numHHH_true

		precision_ave /= float(self.Tc)
		recall_ave /= float(self.Tc)
		num_HHH /= float(self.Tc)
		return [recall_ave, precision_ave, num_HHH]
			 			 
							
	### encapsulate results
	def calMetrics(self):
		result = []
		NMSE = self.calNMSE()
		result.append(NMSE)
		
		for value in self.calHHI():
			result.append(value)

		for value in self.calHHHI():
			result.append(value)

		return result
		
	
if __name__ == "__main__":
	pass	
