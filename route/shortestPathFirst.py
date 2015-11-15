import heapq

class Solution(object):
	def __init__(self, Graph):
		self.graph = Graph
		self.graph.clean()

	def dijkstra(self, dst):
		# clean graph
		self.graph.clean()

		# initialize dst node
		dst_node = self.graph.get_node(dst)	
		dst_node.set_distance(0)
		dst_node.set_predecessor(None)

		heap = []
		pre = None
		heapq.heappush(heap, (dst_node.get_distance(), dst))
		while (heap != []):
			# retire one node from heapq: find the shortest path for that node
			(shortest, node_id) = heapq.heappop(heap)
			curr_node = self.graph.get_node(node_id)
			curr_node.set_visited()
		
			# update distance for neighboring nodes of this "retired" node
			for adj in curr_node.get_connections():
				adj_node = self.graph.get_node(adj)
				# if adj hasn't retired, update distance
				if not adj_node.get_visited():
					# directed graph
					tmp_distance = curr_node.get_distance() + adj_node.get_edge_weight(node_id)
					if adj_node.get_distance() > tmp_distance:
						adj_node.set_distance(tmp_distance)
						adj_node.set_predecessor(node_id)
			
			# rebuild heapq
			# 1. pop every item
			while(len(heap)):
				heapq.heappop(heap)
			# 2. push all vertices not visited into the queue
			for v in self.graph:
				if not v.get_visited():
					heapq.heappush(heap, (v.get_distance(), v.get_id()))				

	
	def shortestPathFirst(self, src, dst):
		path = []
		path.append(src)
		pre = self.graph.get_node(src).get_predecessor()
		while(pre != None):
			path.append(pre)
			pre = self.graph.get_node(pre).get_predecessor()
		return path	
