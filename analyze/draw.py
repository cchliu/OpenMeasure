import matplotlib.pyplot as plt


class Draw(object):
	def __init__(self, outfile):
		self.fig = plt.figure()
		#self.fig, self.axes = plt.subplots(nrows=numrows, ncols=numcols, sharex=True, sharey=True)
		self.ax = self.fig.add_subplot(1, 1, 1)
		self.outfile = outfile


	def draw(self, x, y):
		self.ax.plot(x, y)


	def draw_bar(self, x, y, barWidth=0.35):
		self.ax.bar(x, y, barWidth, color = 'b')
		 

	def multidraw_subplot(self, x, multi_y, numrows, numcols, legend):
		for idx, y in enumerate(multi_y):	
			ax_tmp = self.fig.add_subplot(numrows, numcols, idx+1)
			ax_tmp.plot(x, y, label=legend[idx])
			ax_tmp.legend(loc='best')
		self.ax.spines['top'].set_color('none')
		self.ax.spines['bottom'].set_color('none')
		self.ax.spines['left'].set_color('none')
		self.ax.spines['right'].set_color('none')
		self.ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')


	def multidraw_bar_subplot(self, x, multi_y, numrows, numcols, legend, barWidth=0.35):
		for idx, y in enumerate(multi_y):	
			ax_tmp = self.fig.add_subplot(numrows, numcols, idx+1)
			ax_tmp.bar(x, y, barWidth, label=legend[idx])
			ax_tmp.legend(loc='best')
		self.ax.spines['top'].set_color('none')
		self.ax.spines['bottom'].set_color('none')
		self.ax.spines['left'].set_color('none')
		self.ax.spines['right'].set_color('none')
		self.ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')


	def multidraw_oneplot(self, x, multi_y, ydelta, legend):
		base = 0
		for idx, y in enumerate(multi_y):
			tmp = [k+base for k in y]
			self.ax.plot(x, tmp, label=legend[idx])
			base += ydelta
		self.ax.legend(loc='best')	
		

	def set_xlabel(self, string):
		self.ax.set_xlabel(string)


	def set_ylabel(self, string):
		self.ax.set_ylabel(string)


	def set_title(self, string):
		self.ax.set_title(string)
	

	def savefig(self):
		self.fig.savefig(self.outfile) 
	
		
if __name__ == "__main__":
	pass

