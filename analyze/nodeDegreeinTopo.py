# Calculate Node degree in topology

import matplotlib.pyplot as pl
import pickle

import draw

infile = '../Geant/Geant_graph.pkl'

def main(infile):
	with open(infile, 'rb') as ff:
		G = pickle.load(ff)

	nodeDegree = {}
	for node in G:
		swID = node.get_id()
		nodeDegree[swID] = len(node.get_connections()) + 1 # plus its own subnet

	outfile = 'nodeDegreeinTopo.jpg'
	fig = draw.Draw(outfile)	# create Draw object
	x = sorted([swID for swID in nodeDegree.keys()])
	y = [nodeDegree[swID] for swID in x]

	fig.draw_bar(x, y)
	fig.set_title('Node degrees in topology, Geant')
	fig.set_xlabel('Switch ID')
	fig.set_ylabel('Degrees')
	fig.savefig()


if __name__ == "__main__":
	main(infile)		
