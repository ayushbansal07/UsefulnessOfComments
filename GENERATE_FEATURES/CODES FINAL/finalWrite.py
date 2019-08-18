import csv
import os

def readCSV(fname):
	f = open(fname, 'r')
	r = csv.reader(f)
	out = []
	for each in r:
		out.append(each)
	f.close()
	return out

def writeCSV(fname, csvloc):
	output = readCSV(csvloc)
	ofileloc = fname.replace("/", "_")
	os.system("sudo cp " + fname + " " + "CSV/" + ofileloc) 
	outfile = open("CSV/" + ofileloc + "_excel.csv", 'wb')
	writer = csv.writer(outfile , delimiter = ',', quoting = csv.QUOTE_NONNUMERIC)
	for eachrow in output: 
		writer.writerow(eachrow)
	outfile.close()

import sys
if len(sys.argv) != 3:
	print "Give two arguments which is C filename and csv location"
	exit(-1)

fname = sys.argv[1]
csvloc = sys.argv[2]
writeCSV(fname, csvloc)
