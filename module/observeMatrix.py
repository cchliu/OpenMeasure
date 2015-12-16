""" Setup Observation Matrix """
import numpy as np
import math
import operator
from copy import deepcopy
from gurobiSolver import sw_fl_alloc 

class observeMatrix(object):
	def __init__(self, sw_route, flow_route, SDNSwitchList, num_flows):
		self.swRoute = sw_route
		self.flowRoute = flow_route
		self.SDNSwitchList = SDNSwitchList
		self.swHj = {}
		self.swLinkLoad = {}
		self.numFlows = num_flows


	### SNMP link load
	def initLinkLoad_multi(self):
		for sw in self.swRoute:
			ports = sorted([int(k) for k in self.swRoute[sw]])
			mj = len(ports)
			tmp_LL = np.zeros([mj, self.numFlows])
			row = 0
			for port in ports:
				for fl in self.swRoute[sw][str(port)]:
					tmp_LL[row][fl] = 1
				row += 1
			self.swLinkLoad[int(sw)] = tmp_LL
		return self.swLinkLoad


	### SDNSwitchList: routing entries based on destination 
	def SDNSwitchRoutingEntries_multi(self):
		numIPs = int(math.sqrt(self.numFlows))
		for sw in self.SDNSwitchList:
			routeRule = {}
			ports = sorted([int(k) for k in self.swRoute[str(sw)]])
			for port in ports:
				for fl in self.swRoute[str(sw)][str(port)]:
					dstIP = fl / numIPs + 1
					if not (port, dstIP) in routeRule:
						routeRule[(port, dstIP)] = [fl]
					else:
						routeRule[(port, dstIP)].append(fl)

			tmp_H = np.zeros([len(routeRule.keys()), self.numFlows])
			row = 0
			for key in routeRule:
				for fl in routeRule[key]:
					tmp_H[row][fl] = 1
				row += 1
			self.swHj[sw] = tmp_H
		return self.swHj

  			 
	### static aggregation: MLRF
	def MLRF_multi(self, sw_Kj):
		# swHj: prepopulated routing entries
    		# swkj: number of available measuring entries
    		for sw in self.swHj:
        		tmp_Hj = deepcopy(self.swHj[sw])
        		kj = sw_Kj[sw]
        		while kj>0 :
        			candidate = []
            			# find current maximum load entries
            			load_max = 0
            			for i in range(len(tmp_Hj)):
                			load_tmp = sum(tmp_Hj[i])
                			if load_tmp > load_max:
                    				load_max = load_tmp

            			for i in range(len(tmp_Hj)):
                			if sum(tmp_Hj[i]) == load_max:
                    				candidate.append(i)
            			entry = np.random.permutation(candidate)[0]

            			# separate one rule to two rules
            			tmp_list = []
            			for k in range(self.numFlows):
                			if tmp_Hj[entry][k] == 1:
                    				tmp_list.append(k)
            			tmp_list = np.random.permutation(tmp_list).tolist()

            			# modify the old rule
            			length = (len(tmp_list)+1) / 2
            			for fl in tmp_list[0:length]:
                			tmp_Hj[entry][fl] = 0

            			# generate a new rule
            			new_rule = np.zeros((1, self.numFlows), dtype = np.int)
            			for fl in tmp_list[0:length]:
                			new_rule[0][fl] = 1

            			tmp_Hj = np.concatenate((tmp_Hj, new_rule), axis=0)
            			#print "during modification: ", tmp_Hj
            			# available TCAMs minus 1
            			kj = kj-1

        		self.swHj[sw] = tmp_Hj
    		return self.swHj

	
	def setupOM(self):
		swList = sorted([int(sw) for sw in self.swLinkLoad])
		if not len(swList):
			print "Error: No switches"
		D = deepcopy(self.swLinkLoad[swList[0]]) # make a copy so that swLinkLoad won't change
		for sw in swList[1:]:
			D = np.concatenate((D, self.swLinkLoad[sw]), axis=0)

		# OF switch routing entries
		for sw in self.swHj:
			D = np.concatenate((D, self.swHj[sw]), axis=0)
		return D

	
	### Last-Hop Rule Placement ALGO
	### @parameter: checkRank: check rank increase
	def LastHop(self, index, sw_Kj, checkRank):
		# copy sw_Kj: number of available TCAMs at OF switches
		tmp_Kj = {}
		for sw in sw_Kj:
			tmp_Kj[sw] = sw_Kj[sw]

		sw_bj = {} #key: swId, value: flowNum
		for sw in self.SDNSwitchList:
			sw_bj[sw] = []

		# reconstruct local SNMP Linkloads and routing matrix
		self.SDNSwitchRoutingEntries_multi()
		D = self.setupOM()
		
		print "rank of matrix, SNMP Linkloads + Routing Entries: ", np.linalg.matrix_rank(D)
		
		# total number of measuring entries
		K = sum([sw_Kj[sw] for sw in self.SDNSwitchList])

		for fl in index:
			switches = self.flowRoute[str(fl)]
			# install @ the last switch, move forward hop-by-hop if no space
			for sw in switches[::-1]:
				if sw in self.SDNSwitchList and tmp_Kj[sw] > 0: # available to install
					B = np.zeros([1,self.numFlows], dtype=np.int)
					B[0][fl] = 1

					if checkRank == True:
						tmp_D = np.concatenate((D, B), axis=0)
						# check if rank increased
						if np.linalg.matrix_rank(tmp_D) == np.linalg.matrix_rank(D) + 1:
							D = tmp_D
							tmp_Kj[sw] -= 1
							sw_bj[sw].append(fl)
							break
					else:
						D = np.concatenate((D, B), axis = 0)
						tmp_Kj[sw] -= 1
						sw_bj[sw].append(fl)
						break

			if sum([tmp_Kj[sw] for sw in self.SDNSwitchList]) == 0:
				break
		""" Debug """
		print "rank of network-wide observation matrix after OpenMeasure (LastHop): ", np.linalg.matrix_rank(D)
		return (sw_bj, D)

	
	### Greedy Rule Placement ALGO
	### @parameter: checkRank: check rank increase
	def Greedy(self, index, sw_Kj, checkRank):
		# copy sw_Kj, number of available TCAMs at OF switches
		tmp_Kj = {}
		for sw in sw_Kj:
			tmp_Kj[sw] = sw_Kj[sw]

		sw_bj = {}
		for sw in self.SDNSwitchList:
			sw_bj[sw] = []
	
		# largeFlow coverage
		swLFC = {}
		for sw in self.SDNSwitchList:
			swLFC[sw] = 0
		for fl in index[0:200]:
			switches = self.flowRoute[str(fl)]
			for sw in self.SDNSwitchList:
				if sw in switches:
					swLFC[sw] += 1
		
		# reconstruct local SNMP LinkLoads and routing matrix
		self.SDNSwitchRoutingEntries_multi()
		D = self.setupOM()
	
		print "rank of matrix, SNMP Linkloads + Routing Entries: ", np.linalg.matrix_rank(D)
		
		for fl in index:
			switches = self.flowRoute[str(fl)]
			switches = [sw for sw in switches if sw in self.SDNSwitchList]
			
			# sort switch list based on 1)descending orde of Kj 2)ascending order of largeFlow coverage
			tmp = []
			for sw in switches:
				tmp.append((sw, tmp_Kj[sw]))
			
			stmp = sorted(tmp, key=operator.itemgetter(1), reverse=True)
			
			tmp = []
			i = 0
			while(i < len(stmp) and stmp[i][1] == stmp[0][1]):
				tmp.append((stmp[i][0], swLFC[stmp[i][0]]))
				i += 1  
			
			stmp = sorted(tmp, key=operator.itemgetter(1))

			if len(stmp) >0 and tmp_Kj[stmp[0][0]] > 0: # available to install
				curr_sw = stmp[0][0]
                		B = np.zeros((1, self.numFlows), dtype = np.int)
                		B[0][fl] = 1

				if checkRank == True:
                			tmp_D = np.concatenate((D, B), axis = 0)
		                	if np.linalg.matrix_rank(tmp_D) == np.linalg.matrix_rank(D) + 1:
                    				D = tmp_D
                    				tmp_Kj[curr_sw] -= 1
                    				sw_bj[curr_sw].append(fl)
        		
				else:
					D = np.concatenate((D, B), axis=0)
					tmp_Kj[curr_sw] -= 1
					sw_bj[curr_sw].append(fl)

			if sum([tmp_Kj[sw] for sw in tmp_Kj.keys()]) == 0: # used up all TCAMs
            			break

		""" Debug """
		print "rank of network-wide observation matrix after OpenMeasure (Greedy): ", np.linalg.matrix_rank(D)
		return (sw_bj, D)
	

	### directly solve the rule placement ILP
	def ILP(self, weight, sw_Kj):
		sw_bj = {}
		for sw in self.SDNSwitchList:
			sw_bj[sw] = []

		# reconstruct local SNMP Linkloads and routing matrix
		self.SDNSwitchRoutingEntries_multi()
		D = self.setupOM()

		print "rank of matrix, SNMP Linkloads + Routing Entries: ", np.linalg.matrix_rank(D)
			
		sw_fl_matrix = sw_fl_alloc(weight, self.flowRoute, sw_Kj, self.numFlows)
		sw_lst = sorted([sw for sw in sw_Kj])
			
		for idx, sw in enumerate(sw_lst):
			for fl in range(self.numFlows):
				if sw_fl_matrix[idx][fl] == 1:
					sw_bj[sw].append(fl)
					B = np.zeros([1, self.numFlows], dtype=np.int)
					B[0][fl] = 1
					D = np.concatenate((D, B), axis=0)
	
		""" Debug """
		print "rank of network-wide observatin matrix after OpenMeasure (ILP): ", np.linalg.matrix_rank(D)
		return (sw_bj, D)	
					
	
if __name__ == "__main__":
	pass
		
									
