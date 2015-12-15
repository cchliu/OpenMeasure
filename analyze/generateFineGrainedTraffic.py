""" GENERATE FINE GRAINED TRAFFIC DATA AND SW_ROUTE """
import numpy as np
import pickle
import json
import random

import csvread
import graph
from fileParams import *


# assign a set of IP prefixes to each node
IPPrefixesUB = 5 
IPPrefixesLB = 2

# assign a weight for each IP prefixes at each node
IPWeightUB = 50
IPWeightLB = 10

# assign IP prefix to each IP
IPRangeLB= 0
IPRangeUB = 255


def main():
	""" build ip_prefix --- node mapping """
	### load network topology
	with open(topo_file, 'rb') as ff:
		G = pickle.load(ff)
	
	# number of nodes in network topology
	numNodes = G.get_num_nodes()
	
	
	### create IP-to-node mapping 
	IPLabel = 1
	IPtoNode = {} 
	for sw in range(numNodes):
		numIPs = np.random.randint(IPPrefixesLB, IPPrefixesUB)
		weightSum = 0
		for i in range(IPLabel, IPLabel+numIPs):
			weight = np.random.randint(IPWeightLB, IPWeightUB)
			IPtoNode[i] = [sw+1, weight] # swID starting from 1
			weightSum += weight
		
		for i in range(IPLabel, IPLabel+numIPs):
			IPtoNode[i][1] /= float(weightSum)

		IPLabel += numIPs


	# number of fine-grained IPs
	numIPs = IPLabel-1
	# number of fine-grained flows
	numFlows = numIPs * numIPs
	""" Debug """
	print "number of fine-grained IPs: ", numIPs
	print "number of fine-grained flows: ", numFlows

	### load original traffic
	for idx, infile in enumerate(infile_lst):
		tmOrigin = csvread.csvread(infile)

		# number of time intervals
		Tc = len(tmOrigin[0])

		### create fine grained traffic
		traffic = []
		for fl in range(numFlows):
			dstIP = fl / numIPs + 1	
			dstSW = IPtoNode[dstIP][0]
			dstWgt = IPtoNode[dstIP][1]
					
			srcIP = fl % numIPs + 1	
			srcSW = IPtoNode[srcIP][0]
			srcWgt = IPtoNode[srcIP][1]

			flNum = (dstSW-1) * numNodes + (srcSW-1) 
			tmp = [int(round(tmOrigin[flNum][k]*dstWgt*srcWgt)) for k in range(Tc)]
			traffic.append(tmp)

		""" Debug """
		print "number of fine-grained flows: ", len(traffic)
		print "number of time intervals in fine-grained flows: ", len(traffic[0])

		### write fine-grained traffic to file
		csvread.csvwrite(outfile_lst[idx], traffic)

	
	### load original flow_route file
	with open(flow_route_file, 'rb') as ff:
                flow_route = json.load(ff)

	
	### re-generate flow_route for fine-grained flows
	new_flow_route = {}
	for fl in range(numFlows):
		dstIP = fl / numIPs + 1
		dstSW = IPtoNode[dstIP][0]
		dstWgt = IPtoNode[dstIP][1]

		srcIP = fl % numIPs + 1
		srcSW = IPtoNode[srcIP][0]
		srcWgt = IPtoNode[srcIP][1]
		
		flNum = (dstSW-1) * numNodes + (srcSW-1)
		new_flow_route[fl] = flow_route[str(flNum)]
	
	
	### store new_flow_route into file
	with open(output_flow_route_file, 'wb') as ff:
		json.dump(new_flow_route,ff)


	### initiate sw route
        sw_route = {}# key: sw, value: (port, flows)
        for node in G:
                node_id = node.get_id()
                #""" Adjust node_id range starting from 0 """
                #node_id -= 1
                if not (node_id) in sw_route:
                        sw_route[node_id] = {}
                        sw_route[node_id][node_id] = []
                        for adj in node.get_connections():
                                sw_route[node_id][adj] = []

        ### create sw route
        for fl in new_flow_route:
                path = new_flow_route[fl]
                for idx, sw in enumerate(path):
                        if idx == (len(path)-1):
                                sw_route[sw][sw].append(fl)
                        else:
                                adj = path[idx+1]
                                sw_route[sw][adj].append(fl)

        ### store routing
        with open(output_sw_route_file, 'wb') as ff:
                json.dump(sw_route, ff)
						

	### assign ip prefix
	IPPrefix = {}
	IPPrefixList = []
	for ip in range(numIPs):
        	while(True):
                	tmp = random.randint(IPRangeLB, IPRangeUB)
                	if not tmp in IPPrefix:
                	        IPPrefix[tmp] = 1
                	        IPPrefixList.append([tmp])
                	        break

	#outfile = '../Geant/prefix.csv.tmp'
	csvread.csvwrite(prefix_outfile, IPPrefixList)
	


if __name__ == "__main__":
	main()
		
