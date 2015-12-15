"""
Input Module: csv-reader
"""
import csv

def csvread(infile):
	traffic = []
	with open(infile, 'rb') as ff:
		content = csv.reader(ff, delimiter='\t', quoting=csv.QUOTE_NONE)
		for row in content:
			tmp = [int(k) for k in row]
			traffic.append(tmp)
	return traffic


def csvwrite(outfile, traffic):
	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter='\t', quoting=csv.QUOTE_NONE)
		writer.writerows(traffic)


def csvappend(outfile, result):
	with open(outfile, 'ab') as ff:
		writer = csv.writer(ff, delimiter='\t', quoting=csv.QUOTE_NONE)
		writer.writerow(result)		 


# store performance metrics
def writeResults(result, cstr, outfile):
	csvappend(outfile, ["NMSE for TME with {0}".format(cstr), result[0]])
        csvappend(outfile, ["PdHH, PfaHH, numHH for TME with {0}".format(cstr), result[1], result[2], result[3]])
	csvappend(outfile, ["Recall, Precision, numHHH for TME with {0}".format(cstr), result[4], result[5], result[6]])
	
	for i in range(7, len(result)):
		csvappend(outfile, ["Debug Infor: {0}".format(result[i])])


if __name__ == "__main__":
	pass	
