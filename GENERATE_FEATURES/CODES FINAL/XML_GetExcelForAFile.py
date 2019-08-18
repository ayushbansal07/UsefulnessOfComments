import sys
import re
import glob
import os
import shutil

if __name__ == "__main__":
	if len(sys.argv) != 6:
		print("Give 5 arguments: filename, vocab dictionary location, problem domain location, xml file location, absolute source code location - in this order")
		exit(-1)

	filename = sys.argv[1]
	vocab_loc = sys.argv[2]
	prob_loc = sys.argv[3]
	xmlfilename = sys.argv[4]
	cfilename = sys.argv[5]

	if os.path.isfile(filename) == False:
		print("Error", filename, " is not a valid filename")
		exit(-1)

	fName1 = str(filename.replace("/" , "_"))
	fName = ""
	print(fName1)
	if fName1.endswith(".c") :
		fName = fName1.replace(".c" , ".p")
	elif fName1.endswith(".cpp") :
		fName = fName1.replace(".cpp" , ".p")
	else :
		fName = fName1 + ".p"
	print(fName)
	# if os.path.exists("CSV/" + filename.replace("/", "_") + "_train.csv"):
	# 	print("Skipping: ",fName)
	# 	exit(0)
	try :
		x = os.system("python2 XML_CommentExtractor.py " + filename)
		print("CommentExtractor " + str(x))
		#key = input("Hit a key")
		if x != 0 :
			exit(-1)
		print "++++ CommentExtractor succesfully done!\n\n\n"

		x = os.system("python2 XML_ScopeModule.py " + filename)
		if x != 0 :
			exit(-1)
		print "++++ ScopeModule succesfully done!\n\n\n"

		os.chdir("Identifier/")
		print xmlfilename, cfilename
		x = os.system("python2 xmlparser.py ../" + xmlfilename + " " + cfilename + " ../" + vocab_loc + " ../" + prob_loc)
		if x != 0:
			exit(-1)
		print "++++ Identifier succesfully done!\n\n\n"
		os.chdir("../")

		x = os.system("python2 XML_FinalExcelGeneration.py " + filename + " " + vocab_loc + " " + prob_loc)
		if x != 0:
			exit(-1)
		print "++++ Knowledge base generation done!\n\n\n"

		os.chdir("FeatureDescOp/")
		x = os.system("python2 classify_batched.py ../knowledge_base.csv")
		if x != 0:
			exit(-1)
		print "++++ Feature generation of Description/Operation succesfully done!\n\n\n"
		os.chdir("../")

		x = os.system("python2 finalWrite.py " + filename + " knowledge_base.csv")
		if x != 0:
			exit(-1)
		print "++++ Excel written done finally\n\n\n"


		excel_file = "CSV/" + filename.replace("/", "_") + "_excel.csv"
		x = os.system("python2 XML_getFeatures.py " + excel_file)
		if x != 0:
			exit(-1)
		print "++++ Features generation done succesfully\n\n\n"

		features_file = excel_file.replace("excel", "feature")
		x = os.system("python2 XML_getFinalFeatures.py " + excel_file + " " + features_file)
                if x != 0:
                        exit(-1)
                print "++++ Build Categories done succesfully\n\n\n"

	except Exception as e :
		print("Error in running the command " + str(e))
		exit(-1)
	exit(0)
