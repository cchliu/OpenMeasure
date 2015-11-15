import xml.etree.ElementTree as ET
import csv
import networkx as nx
import matplotlib.pyplot as plt
import pickle

import graph


infile = '../Geant-topology-anonymised.xml'
vertices = []
edges = []

### Parse Geant topology saved in xml file
def topo_parse_xml(infile):
	doc = ET.parse(infile)
	topo = doc.find("topology")
	
	# parse nodes
	nodes = topo.find("nodes")
	for node in nodes:
		vertices.append(int(node.attrib["id"]))
	
	# parse edges
	links = topo.find("links")
	for link in links:
		tmp = link.attrib["id"].split("_")
		edges.append([int(k) for k in tmp])
	

### Helper function: check undirected graph
def check_link_symmetry():
	for pair in edges:
		sym_pair = [pair[1], pair[0]]
		if not sym_pair in edges:
			print "Info: directed graph in topo"
	print "Info: undirected graph in topo" 


### Helper function: draw topology
def draw_topo(outfile):
	# Create networkx graph
	G = nx.Graph()

	# Add nodes
	for node in vertices:
		G.add_node(node)

	# Add edges
	for edge in edges:
		G.add_edge(edge[0], edge[1])

	# Draw graph
	pos = nx.shell_layout(G)
	nx.draw(G, pos)

	# Save graph
	plt.savefig(outfile)

### Save Geant topology in .pkl file
def main():
	topo_parse_xml(infile)
	check_link_symmetry()
	
	""" Info """
	print sorted(vertices)
	print "Number of nodes in Geant topo: ", len(vertices)
	print "Number of edges in Geant topo: ", len(edges)

	outfile = 'Geant_topo.jpg'
	draw_topo(outfile)

	""" Save Graph """
	G = graph.Graph()
	for v in vertices:
		G.add_vertex(v)

	for edge in edges:
		G.add_edge(edge[0], edge[1], 1)

	""" Info """
	print "Info: Number of nodes in Geant topo:", G.get_num_nodes()
	
	graph_file = "Geant_graph.pkl"
	with open(graph_file, 'wb') as ff:
		pickle.dump(G, ff)

if __name__ == "__main__":
	main()
