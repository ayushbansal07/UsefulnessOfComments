import csv
import pickle

def readCSV(fname):
	f = open(fname, 'r')
	r = csv.reader(f, delimiter = ',', quotechar = '"' , quoting = csv.QUOTE_MINIMAL)
	out = []
	for each in r:
		out.append(each)
	f.close()
	return out


def clubFiles(fname):
	f = open(fname, 'r')
	text = f.read()
	f.close()
	text = text.split("\n")
	
	features = []
	for file in text:
		if file == "":
			break
		data = readCSV(file)
		features.extend(data)
	
	ofname = sys.argv[2]
	f = open(ofname, 'w')
	writer = csv.writer(f, delimiter=',', quotechar = '"', quoting=csv.QUOTE_NONNUMERIC)
	for each in features:
		writer.writerow(each)
	f.close()

import sys
if len(sys.argv) != 3:
	print "Give two arguments 1) the location of the file which contains all the files to be clubbed 2) the location of output file"
	exit(-1)
clubFiles(sys.argv[1])
