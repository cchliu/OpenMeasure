import os
import sys
import json
import numpy as np
curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(curr_dir + '/module/script')


import csvread
from observeMatrix import observeMatrix
from pullingTimeIntervals import PullTimeIntervals

class OpenMeasure(object):
	def __init__(self, tmfile, sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao):
		self.tmfile = tmfile
		self.swRouteFile = sw_route_file
		self.flowRouteFile = flow_route_file
		self.SDNSwitchList = SDNSwitchList
		self.prefixFile = prefix_file
		self.Tao = Tao

	
	def loadFile(self):
		### load ground truth traffic
		traffic = csvread.csvread(self.tmfile)
		# aggregate traffic within pulling time intervals
                aggreTM = PullTimeIntervals(self.Tao)
		self.tmTrue = aggreTM.aggregateTraffic(traffic)

		"""
		#some experiments on the traffic data
		#offset = 146+20
		#self.tmTrue = [row[offset:] for row in self.tmTrue]
		
		origin = [row[0] for row in self.tmTrue]
		offset = 5000
		K = 120
		tmp = []
		while(True):
			tmp = np.random.permutation(origin[0:offset])
			tmp = tmp.tolist()
			for i in range(offset,len(origin)):
				tmp.append(origin[i])

			index_origin = sorted(range(len(origin)), key = lambda k: origin[k], reverse=True)[0:K]
			index_tmp = sorted(range(len(origin)), key = lambda k: tmp[k], reverse=True)[0:K]
			match = sum([1 for k in index_tmp if k in index_origin])
			match = match / float(K) * 100
			print match
			break
			#if(match >= 60 and match <= 100):
			#	break

		for fl in range(len(origin)):
			self.tmTrue[fl][0] = tmp[fl]
		
		self.tmTrue = [row[0:200] for row in self.tmTrue]	
		"""
	
		self.N = len(self.tmTrue) # number of flows
		self.Tc = len(self.tmTrue[0]) # number of time intervals
		
		""" Debug """
		print "after postprocessing "
		print "number of flows for tmTrue: ", self.N
		print "number of time intervals for tmTrue: ", self.Tc

		### load sw_route & flow_route
		with open(self.swRouteFile, 'rb') as ff:
			self.swRoute = json.load(ff)

		with open(self.flowRouteFile, 'rb') as ff:
			self.flowRoute = json.load(ff)
		
		### load IP prefix
		self.IPPrefix = csvread.csvread(self.prefixFile) 


	def popSNMPLinkLoad(self):
		### create observeMatrix object
		self.OM = observeMatrix(self.swRoute, self.flowRoute, self.SDNSwitchList, self.N)
		
		### initiate SNMP Linkloads entries
		swLinkLoad = self.OM.initLinkLoad_multi()
		M = 0 # count number of SNMP Linkloads entries
		for sw in swLinkLoad:
			mj = len(swLinkLoad[sw])
			M += mj

		print "total number of SNMP link load entries: ", M


if __name__ == "__main__":
	pass		
		 
