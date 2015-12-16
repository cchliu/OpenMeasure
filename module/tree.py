""" IP Prefix Hierarchical Tree """
import copy

class Node(object):
	def __init__(self):
		self.left = None
		self.right = None
		self.pointer = -1
		self.pattern = "********"
		self.value = 0
		self.isHHH = 0 # 1: isHHH, 0: not HHH
		self.HHH_val = 0
		self.nodeID = 0


	def setNodeID(self, ID):
		self.nodeID = ID


	def getNodeID(self):
		return self.nodeID

		
	def setPointer(self, num):
		self.pointer = num


	def setBit(self, binary):
		patternList = list(self.pattern)
		patternList[self.pointer] = str(binary)
		self.pattern = "".join(patternList)

	def setPattern(self, pat):
		self.pattern = pat


	def setIsHHH(self, binary):
		self.isHHH = binary


	def setHHHVal(self, val):
		self.HHH_val = val


	def getHHHVal(self):
		return self.HHH_val


	def getVal(self):
		return self.value

	
class HTree(object):
	def __init__(self, bitLenth=8): 
		self.bitLenth = 8
		self.startNum = 1000
		self.head = Node()


	# recursively create hierarchical tree
	def create(self, node):
		node.setNodeID(self.startNum)
		self.startNum += 1
		if node.pointer + 1 < self.bitLenth:
			node.left = Node()
			node.left.setPointer(node.pointer + 1)
			node.left.setPattern(node.pattern)
			node.left.setBit(0)
			self.create(node.left)

			node.right = Node()
			node.right.setPointer(node.pointer + 1)
			node.right.setPattern(node.pattern)
			node.right.setBit(1)
			self.create(node.right)
		return

	
	# recursively clear tree 
	def clear(self, node):
		if node == None:
			return
		node.value = 0
		node.HHH_val = 0
		node.isHHH = 0
		self.clear(node.left)
		self.clear(node.right)
	

	# insert a flow size into the tree
	def fill(self, Prefix, size):
		self.head.value += size
		tmpNode = self.head
		for i in range(self.bitLenth):
			if Prefix[i] == 1:
				tmpNode = tmpNode.left
				tmpNode.value += size
			elif Prefix[i] == 0:
				tmpNode = tmpNode.right
				tmpNode.value += size
	

	# recursively plot the tree
	def plot(self, node):
		if node == None:
			return
		if node.isHHH == 1:
			print node.pattern, node.nodeID, node.value, node.isHHH, node.HHH_val
		self.plot(node.left)
		self.plot(node.right)


if __name__ == "__main__":
	pass		
