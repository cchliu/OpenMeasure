import os
import sys
import numpy as np
import json
from multiprocessing import Process, Queue

curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(curr_dir + '/module/script')
#print curr_dir + '/module/'

import csvread
from selectSDNSwitch import selectSDNSwitch
from TMEwSNMPLinkLoadOnly import TMEwSNMPLinkLoad
from TMEaddRoutingEntries import TMEaddRoutingEntries
from TMEwRS import TMEwRS
from TMEwMLRF import TMEwMLRF
from TMEwLFF import TMEwLFF
from TMEideal import TMEideal
from TMEwLB import TMEwLB
from TMEwWLP import TMEwWLP
from TMEwMUCBP import TMEwMUCBP

from fileParams import *

K = 0
recordsNum = 0
Res = 15	# mins
Tao = 15

#SDNSwitchList = [2, 5, 10, 12, 16, 17]
SDNSwitchList = [1, 2, 3, 5, 9, 10]
#SDNSwitchList = [1, 2, 3, 5, 10, 12]

def commandline_reminder():
        global K, Tao, recordsNum
        print "please enter the number of TCAM entries available for direct measurement, K>0"
        K = int(raw_input())

        print "please enter the number of pulling time intervals, in the unit of times of Res"
        Tao = int(raw_input())

        print "please enter the number of records needed to be maintained"
        recordsNum = int(raw_input())


def worker(q, iters, obj, sw_Kj, f1, f2):
	f1(sw_Kj)
	for i in range(iters):
		if i == 0:
			result = f2()
		else:
			tmp = f2()
			for j in range(len(result)):
				result[j] += tmp[j] 
	
	for j in range(len(result)):
		result[j] /= float(iters)

	q.put([obj.cstr, result])


def main():
	commandline_reminder()
	
	outfile = 'output/scaleNewGeantTraces_2week_result.txt'
	kj_lst = [20, 40, 60, 80, 100, 120, 140, 160]
	num_cores = len(kj_lst)
	sw_Kj = {}

	#selectSDNSwitch(infile_lst[0], flow_route_file, Tao)

	
	
	### TME w/ only SNMP LinkLoad 	
	case1 = TMEwSNMPLinkLoad(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
	result = case1.TMEwSNMPLinkLoad()
	csvread.writeResults(result, case1.cstr, outfile) 
	

	### TME w/ SNMP LinkLoads + Routing Entries
	case2 = TMEaddRoutingEntries(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
        result = case2.TMEaddRoutingEntries()
	csvread.writeResults(result, case2.cstr, outfile)


	### TME w/ Random Scheme
	sw_Kj = {}
	kj = 20
	for sw in SDNSwitchList:
		sw_Kj[sw] = 20
	case3 = TMEwRS(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
	case3.set_rulePlacementAlgo("LastHop")
	case3.set_swKj(sw_Kj)
	result = case3.TMEwRS()
	csvread.writeResults(result, case3.cstr, outfile)
 	

	iters = 1
	q = Queue()
	for idx, i in enumerate(kj_lst):
		kj = kj_lst[idx]
		for sw in SDNSwitchList:
			sw_Kj[sw] = kj
		tmp_case = TMEwRS(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
		tmp_case.set_rulePlacementAlgo("LastHop")
		p = Process(target=worker, args=(q, iters, tmp_case, sw_Kj, tmp_case.set_swKj, tmp_case.TMEwRS))
		p.start()

	for i in range(num_cores):
		tmp_result = q.get()
		csvread.writeResults(tmp_result[1], tmp_result[0], outfile)		


	### TME w/ MLRF		
	sw_Kj = {}
	kj = 20
	for sw in SDNSwitchList:
		sw_Kj[sw] = 20
	case4 = TMEwMLRF(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
	case4.set_swKj(sw_Kj)
        result = case4.TMEwMLRF()
	csvread.writeResults(result, case4.cstr, outfile)


	iters = 50
        q = Queue()
        for idx, i in enumerate(kj_lst):
                kj = kj_lst[idx]
                for sw in SDNSwitchList:
                        sw_Kj[sw] = kj
		tmp_case = TMEwMLRF(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
                p = Process(target=worker, args=(q, iters, tmp_case, sw_Kj, tmp_case.set_swKj, tmp_case.TMEwMLRF))
                p.start()

        for i in range(num_cores):
                tmp_result = q.get()
		csvread.writeResults(tmp_result[1], tmp_result[0], outfile)
	

	### TME w/ LFF	
	sw_Kj = {}
	kj = 20
	for sw in SDNSwitchList:
		sw_Kj[sw] = kj
	case5 = TMEwLFF(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
	case5.set_rulePlacementAlgo("ILP")
	case5.set_swKj(sw_Kj)
	result = case5.TMEwLFF()
	csvread.writeResults(result, case5.cstr, outfile)	

		
	sw_Kj = {}
	iters = 1
	q = Queue()
	for idx, i in enumerate(kj_lst):
		kj = kj_lst[idx]
		for sw in SDNSwitchList:
			sw_Kj[sw] = kj
		tmp_case = TMEwLFF(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
		tmp_case.set_rulePlacementAlgo("ILP")
		p = Process(target=worker, args=(q, iters, tmp_case, sw_Kj, tmp_case.set_swKj, tmp_case.TMEwLFF))
		p.start()

	for i in range(num_cores):
		tmp_result = q.get()
		csvread.writeResults(tmp_result[1], tmp_result[0], outfile)


	### TME w/ ideally measuring Top Flows w/o rule placement restrictions	
	sw_Kj = {}
	kj = 60
	for sw in SDNSwitchList:
		sw_Kj[sw] = kj
	case6 = TMEideal(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
        case6.set_swKj(sw_Kj)
        result = case6.TMEideal()
        csvread.writeResults(result, case6.cstr, outfile)


	iters = 1
        q = Queue()
        for idx, i in enumerate(kj_lst):
                kj = kj_lst[idx]
                for sw in SDNSwitchList:
                        sw_Kj[sw] = kj
                tmp_case = TMEideal(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
                p = Process(target=worker, args=(q, iters, tmp_case, sw_Kj, tmp_case.set_swKj, tmp_case.TMEideal))
                p.start()

        for i in range(num_cores):
                tmp_result = q.get()
                csvread.writeResults(tmp_result[1], tmp_result[0], outfile)
	
	
	### TME w/ ideal large flow prediction w/ rule placement restrictions
	sw_Kj = {}
        kj = 120
        for sw in SDNSwitchList:
                sw_Kj[sw] = kj
        case7 = TMEwLB(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
	case7.set_rulePlacementAlgo("LastHop")
        case7.set_swKj(sw_Kj)
        result = case7.TMEwLB()
        csvread.writeResults(result, case7.cstr, outfile)
	

	iters = 1
	q = Queue()
	for idx, i in enumerate(kj_lst):
		kj = kj_lst[idx]
		for sw in SDNSwitchList:
			sw_Kj[sw] = kj
		tmp_case = TMEwLB(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
		tmp_case.set_rulePlacement("LastHop")
		p = Process(target=worker, args=(q, iters, tmp_case, sw_Kj, tmp_case.set_swKj, tmp_case.TMEwLB))
		p.start()

	for i in range(num_cores):
		tmp_result = q.get()
		csvread.writeResults(tmp_result[1], tmp_result[0], outfile)


	### TME w/ OpenMeasure (WLP)
	print recordsNum
	sw_Kj = {}
	kj = 20
	for sw in SDNSwitchList:
		sw_Kj[sw] = kj	
	case8 = TMEwWLP(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
	case8.set_rulePlacementAlgo("LastHop")
	case8.set_swKj(sw_Kj)
	case8.set_recordsNum(recordsNum)
	result = case8.TMEwWLP()
	csvread.writeResults(result, case8.cstr, outfile)
		
		
	iters = 1
	#for method in ["ILP"]:
	for method in ["ILP", "LastHop", "Greedy"]:
		q = Queue()
		for idx, i in enumerate(kj_lst):
			kj = kj_lst[idx]
			for sw in SDNSwitchList:
				sw_Kj[sw] = kj
			tmp_case = TMEwWLP(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
			tmp_case.set_rulePlacementAlgo(method)
			tmp_case.set_recordsNum(recordsNum)

			p = Process(target=worker, args=(q, iters, tmp_case, sw_Kj, tmp_case.set_swKj, tmp_case.TMEwWLP))
			p.start()
		
		for i in range(num_cores):
			tmp_result = q.get()
			csvread.writeResults(tmp_result[1], tmp_result[0], outfile)

	
	### TME w/ OpenMeasure (MUCBP)
	sw_Kj = {}
	kj = 20
	for sw in SDNSwitchList:
		sw_Kj[sw] = kj
	case9 = TMEwMUCBP(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
	case9.set_rulePlacementAlgo("ILP")
	case9.set_swKj(sw_Kj)
	case9.set_windowSize(0)
	result = case9.TMEwMUCBP()
	csvread.writeResults(result, case9.cstr, outfile)
	

	sw_Kj = {}
	iters = 1
	for method in ["LastHop", "Greedy", "ILP"]:
		q = Queue()
		for idx, i, in enumerate(kj_lst):
			kj = kj_lst[idx]
			for sw in SDNSwitchList:
				sw_Kj[sw] = kj
			tmp_case = TMEwMUCBP(infile_lst[0], sw_route_file, flow_route_file, prefix_file, SDNSwitchList, Tao)
			tmp_case.set_rulePlacementAlgo(method)
			tmp_case.set_windowSize(0)
			
			p = Process(target=worker, args=(q, iters, tmp_case, sw_Kj, tmp_case.set_swKj, tmp_case.TMEwMUCBP))
			p.start()
	
		for i in range(num_cores):
			tmp_result = q.get()
			csvread.writeResults(tmp_result[1], tmp_result[0], outfile)
	

if __name__ == "__main__":
	main()
