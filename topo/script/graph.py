""" Graph Class """
import sys

class Vertex(object):
	def __init__(self, node_id):
		self.node_id = node_id
		""" Key: node_id, Value: edge weight """
		self.adjacents = {}
		self.distance = sys.maxint
		self.predecessor = None
		self.visited = 0

	
	def add_adjacent(self, adj_id, weight):
		 if not adj_id in self.adjacents:
			self.adjacents[adj_id] = weight

	
	def set_distance(self, distance):
		self.distance = distance


	def reset_distance(self):
		self.distance = sys.maxint
	

	def get_distance(self):
		return self.distance


	def set_predecessor(self, pre):
		self.predecessor = pre


	def reset_predecessor(self):
		self.predecessor = None


	def get_predecessor(self):
		return self.predecessor


	def set_visited(self):
		self.visited = 1

	
	def reset_visited(self):
		self.visited = 0


	def get_visited(self):
		return self.visited


	def get_connections(self):
		return self.adjacents.keys()


	def get_id(self):
		return self.node_id


	def get_edge_weight(self, adj_id):
		return self.adjacents[adj_id]


class Graph(object):
	def __init__(self):
		self.num_nodes = 0
		""" Key: node_id, Value: Vertex(node_id) """
		self.nodes = {}
	

	def __iter__(self):
		return iter(self.nodes.values())


	# Add a node
	def add_vertex(self, node_id):
		if not node_id in self.nodes:
			self.nodes[node_id] = Vertex(node_id)
			self.num_nodes += 1


	# Add an edge (directed)
	def add_edge(self, frm, to, weight):
		if not frm in self.nodes:
			print "Node {0} not in graph, create node {1} now ... ".format(frm, frm)
			self.nodes[frm] = Vertex(frm)

		if not to in self.nodes:
			print "Node {0} not in graph, create node {1} now ... ".format(to, to)
			self.nodes[to] = Vertex(to)

		self.nodes[frm].add_adjacent(to, weight)

	
	def get_node(self, node_id):
		return self.nodes[node_id]

	
	def get_num_nodes(self):
		return self.num_nodes


	def clean(self):
		""" reset distances and predecessors """
		for v in self:
			v.reset_distance()
			v.reset_predecessor()
			v.reset_visited()


	def plot(self):
		print "Graph Data: "
		for v in self:
			for w in v.get_connections():
				vid = v.get_id()
				wid = w
				print " ( %s, %s, %3d)" % (vid, wid, v.get_edge_weight(w))
