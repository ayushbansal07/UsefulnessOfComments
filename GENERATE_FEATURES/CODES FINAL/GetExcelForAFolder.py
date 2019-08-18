import os
import csv
import json
import sys

def visitor(filters, dirname, names):
	mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
	for name in mynames:
		fpath = os.path.join(dirname, name)
		if not os.path.isdir(fpath):
			os.system("python2 GetExcelForAFile.py " + fpath + " " + sys.argv[2] + " " + sys.argv[3])

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print("Give 3 arguments: folder location, vocab dictionary location, problem domain location in order")
		exit(-1)
	filters = [".c"]
	os.path.walk(sys.argv[1], visitor, filters)
