""" AGGREGATE TRAFFIC WITHIN PULLING TIME INTERVALS """

class PullTimeIntervals(object):
	def __init__(self, Tao):
		self.Tao = Tao


	def aggregateTraffic(self, traffic):
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
                        while (i+self.Tao <= T):
                                tmp.append(sum(traffic[fl][i:i+self.Tao]))
                                i += self.Tao

                        p_traffic.append(tmp)

		if not p_traffic:
			print "Error: No output data"
			return		

		""" Debug """
		print "after aggregate traffic within pulling time intervals"
		print "number of flows in traffic: ", len(p_traffic)
		print "number of columns in traffic: ", len(p_traffic[0]) 
                return p_traffic


if __name__ == "__main__":
	pass
