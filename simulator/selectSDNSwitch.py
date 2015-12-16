""" Select SDN Switches """
import json
import csvread
from pullingTimeIntervals import PullTimeIntervals

def selectSDNSwitch(infile, flow_route_file, Tao):
	# load ground truth traffic
	tmTrue = csvread.csvread(infile)
	aggreTM = PullTimeIntervals(Tao)
	tmTrue = aggreTM.aggregateTraffic(tmTrue)

	# number of flows
	N = len(tmTrue)
	# number of time intervals
	Tc = len(tmTrue[0])

	# load flow_route
	with open(flow_route_file, 'rb') as ff:
		flowRoute = json.load(ff)

	K = 200
	#SDNSwitchList = [1, 2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 17]
	SDNSwitchList = [1, 2, 3, 5, 9, 10]
	hitRate = 0
	t_epoch = 0
	LFCsw = {}
	while(t_epoch < Tc):
		col_true = [row[t_epoch] for row in tmTrue]
		index = sorted(range(len(col_true)), key = lambda k: col_true[k], reverse=True)
				
		for fl in index[0:K]:
			switches = flowRoute[str(fl)]
			for sw in switches:
				if not sw in LFCsw:
					LFCsw[sw] = 1
				else:
					LFCsw[sw] += 1
			match = sum([1 for sw in switches if sw in SDNSwitchList])
			if match >= 1:
				hitRate += 1
		t_epoch += 1

	#for sw in LFCsw:
	#	print "switch ID {0} covers {1} percent of large flows".format(sw, LFCsw[sw]/float(Tc * K))
	print "SDNSwitchList coverage for large flows: {0}".format(hitRate / float(Tc))


	SDNSwitchList = []
	for i in range(1,24):
		SDNSwitchList.append(i)
		hitRate = 0
		print "SDNSwitchList: ", SDNSwitchList

		t_epoch = 0	
		while(t_epoch < Tc):
			col_true = [row[t_epoch] for row in tmTrue]
			index = sorted(range(len(col_true)), key = lambda k: col_true[k], reverse=True)
			
			for fl in index[0:K]:
				switches = flowRoute[str(fl)]
				match = sum([1 for sw in switches if sw in SDNSwitchList])
				if match >= 1:
					hitRate += 1
			t_epoch += 1

		print "SDNSwitchList coverage for large flows: {0}".format(hitRate / float(Tc))

	
        #SDNSwitchList = [1, 2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 17]
        SDNSwitchList = [1, 2, 3, 5, 9, 10]
	#SDNSwitchList = [1, 2, 5, 9, 10, 12]
	for K in [120, 240, 360, 480, 600]:
		hitRate = 0
		
		t_epoch = 0
		while(t_epoch < Tc):
                        col_true = [row[t_epoch] for row in tmTrue]
                        index = sorted(range(len(col_true)), key = lambda k: col_true[k], reverse=True)

                        for fl in index[0:K]:
                                switches = flowRoute[str(fl)]
                                match = sum([1 for sw in switches if sw in SDNSwitchList])
                                if match >= 1:
                                        hitRate += 1
                        t_epoch += 1

                print "SDNSwitchList coverage for large flows: {0} @ K = {1}".format(hitRate / float(Tc), K)

