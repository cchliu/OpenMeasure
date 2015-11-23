import pickle
import graph
import json

import shortestPathFirst


def main():
	# load topo graph
	infile = 'Geant_graph.pkl'
	with open(infile, 'rb') as ff:
		G = pickle.load(ff)

	""" Info """
	num_nodes = G.get_num_nodes()
	print "Info: No. of nodes in the graph: ", num_nodes
	# No. of flows
	N = num_nodes * num_nodes
	print "Info: No. of flows in the graph: ", N


	""" Routing based on Shortest Path First """
	flow_route = {}
	solution = shortestPathFirst.Solution(G)		
	for dst_node in G:
		dst_id = dst_node.get_id()
		solution.dijkstra(dst_id)
		for src_node in G:
			src_id = src_node.get_id()
			flow_num = (dst_id-1) * num_nodes + (src_id-1)
			if not flow_num in flow_route:
				""" In path, node_id range from 1 to 23 """
				flow_route[flow_num] = solution.shortestPathFirst(src_id, dst_id)

	""" Store routing """
	outfile = 'Geant_flow_route.json'
	with open(outfile, 'wb') as ff:
		json.dump(flow_route, ff)		


	""" sw route """
	sw_route = {}# key: sw, value: (port, flows)
	
	""" Initiate sw route """
	for node in G:
		node_id = node.get_id()
		if not (node_id) in sw_route: 
			sw_route[node_id] = {}
			sw_route[node_id][node_id] = []
			for adj in node.get_connections():
				sw_route[node_id][adj] = []
			
	""" Create sw route """	
	for fl in flow_route:
		path = flow_route[fl]
		for idx, sw in enumerate(path):
			if idx == (len(path)-1):
				sw_route[sw][sw].append(fl)
			else:
				adj = path[idx+1]
				sw_route[sw][adj].append(fl)

	""" Store routing """
	outfile = "Geant_sw_route.json"
	with open(outfile, 'wb') as ff:
		json.dump(sw_route, ff)		
			
		

if __name__ == '__main__':
	main()
