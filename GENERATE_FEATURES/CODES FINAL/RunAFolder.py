
import sys
import re
import glob
import os
import csv


''' # Run a folder code 
if __name__ == "__main__":
	for dirname in sys.argv[1:]:
		if os.path.isdir(dirname) == True:
			files = os.listdir(dirname)
			for fl in files:
				if fl.endswith('.c') or fl.endswith('.cpp') :
					if dirname.endswith("/") :
						filename = dirname +  fl
					else :
						filename = dirname + "/" + fl
					try :
						x = os.system("python3 RunAFile.py " + filename)
					except :
						print("Error in RunAFile ")
				

'''

filenames = set()
with open('FinalManualAnnotation.csv', 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')

	for row in reader:
		fname = row[2]
		filenames.add(fname)

processedFiles = list()
with open('FinalValidationResults.csv', 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')

	for row in reader:
		fname = row[0]
		processedFiles.append(fname)

print(len(filenames))

for fl in filenames :
	if fl in processedFiles :
		continue		
	try :
		x = os.system("python3 RunAFile.py " + fl)
	except :
		print("Error in RunAFile ")
	
