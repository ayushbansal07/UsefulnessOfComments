import os
import csv
import json
import sys

def visitor(filters, dirname, names):
	mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
	for name in mynames:
		fpath = os.path.join(dirname, name)
		if not os.path.isdir(fpath):
			os.system("python2 makeCommentsFile.py " + fpath)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Give 1 argument: folder location")
		exit(-1)
	filters = [".c"]
	os.path.walk(sys.argv[1], visitor, filters)
