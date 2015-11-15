# Calculate how many large flows gone through for each switch (Avg across time)
"""
Parameter: 
Dataset resolution Res--- 15min for Geant
Measurement interval Tao --- Tao = Res
K---number of TCAM entries used for direct measuring
n---number of records maintained
"""
import csv
import sys
import math
import matplotlib.pyplot as plt
import json


import csvread
import draw


K = 0
n = 0
Res = 15
Tao = 15
infile_lst = ['../Geant/scaleNewGeantTraces_0108.csv','../Geant/scaleNewGeantTraces_0215.csv','../Geant/scaleNewGeantTraces_0324.csv','../Geant/scaleNewGeantTraces_0401.csv']


def commandline_reminder():
	global K, Tao, n
	print "please enter the number of TCAM entries available for direct measurement, K > 0"
	K = int(raw_input())
	print "please enter the number of pulling time intervals, in the unit of times of Res"
	Tao = int(raw_input())
	#print "please enter the number of records needed to be maintained"
	#n = int(raw_input())


def postprocess_traffic(traffic):
	# postprocess traffic in terms of pulling intervals
	if not traffic:
		print "Error: No input data"
		return

	# number of flows
	N = len(traffic)
	# number of columns
	T = len(traffic[0])
	""" Debug """
	print "before postprocessing"
	print "number of flows in traffic: ", N
	print "number of columns in traffic: ", T

	p_traffic = []
	for fl in range(N):
		i = 0
		tmp = []
		while (i+Tao <= T):
			tmp.append(sum(traffic[fl][i:i+Tao]))
			i += Tao
		
		p_traffic.append(tmp)
	return p_traffic


def process_sw_route(sw_route):
	post_sw_route = {}
	for sw in sw_route:
		post_sw_route[int(sw)] = []
		for adj in sw_route[sw]:
			for fl in sw_route[sw][adj]:
				post_sw_route[int(sw)].append(fl)	
	
	return post_sw_route


def largeFlowThrough(traffic, post_sw_route):
	if not traffic:
		print "Error: No input data"

	# number of flows
	N = len(traffic)
	# number of columns
	T = len(traffic[0])
        """ Debug """
        print "after postprocessing"
        print "number of flows in traffic: ", N
        print "number of columns in traffic: ", T


	sw_lst = sorted([sw for sw in post_sw_route])
	result = [0] * len(sw_lst)

	t_epoch = 0
	while(t_epoch < T):
		curr = [row[t_epoch] for row in traffic]
		index_curr = sorted(range(len(curr)), key = lambda k: curr[k], reverse=True)[0:K] 
		
		for idx, sw in enumerate(sw_lst):
			match = sum([1 for fl in post_sw_route[sw] if fl in index_curr])
			result[idx] += (float(match) / float(K) * 100)

		t_epoch += 1
	
	if(t_epoch != 0):
		result = [float(k) / float(t_epoch) for k in result]
	return result
			

def main():
	commandline_reminder()

	swRouteFile = '../Geant/Geant_sw_route.json'	
	with open(swRouteFile, 'rb') as ff:
		sw_route = json.load(ff)
	
	""" Result for four dataset in Geant"""
	print "Generating largeFlow hitrate for four dataset in GEANT network ..."
	multi_results = []
	ydelta = 0
	numrows = 2
	numcols = 2
	legend = ['Geant_0108', 'Geant_0215', 'Geant_0324', 'Geant_0401']
	for infile in infile_lst:
		traffic = csvread.csvread(infile)
		traffic = postprocess_traffic(traffic)
		post_sw_route = process_sw_route(sw_route)
		result = largeFlowThrough(traffic, post_sw_route)
		multi_results.append(result)
	
	
	outfile = 'largeFlowThroughSwitch.jpg'
	fig = draw.Draw(outfile)	# create Draw object
	x_axis = sorted([int(sw) for sw in sw_route])
	fig.multidraw_bar_subplot(x_axis, multi_results, numrows, numcols, legend)
	fig.set_title('Avg largeFlow through for each switch, GEANT')
	fig.set_xlabel('Switch ID')
	fig.set_ylabel('LargeFlow through (%)')
	fig.savefig()


if __name__ == "__main__":
	main()			
