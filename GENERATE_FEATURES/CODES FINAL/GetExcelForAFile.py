import sys
import re
import glob
import os
import shutil

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print("Give 3 arguments: filename, vocab dictionary location, problem domain location in order")
		exit(-1)
	
	filename = sys.argv[1]
	vocab_loc = sys.argv[2]
	prob_loc = sys.argv[3]
	
	if os.path.isfile(filename) == False or filename.endswith('.c') == False:
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
	try :
		x = os.system("python2 filterFile.py " + filename)
                x = 0
		print("file Filter " + str(x))
                #key = input("Hit a key")
                if x != 0 :
                        exit(-1)
                print "++++ File Filter succesfully done!\n\n\n"

		x = os.system("python2 CommentExtractor.py " + filename)
		print("CommentExtractor " + str(x))
		#key = input("Hit a key")
		if x != 0 :
			exit(-1)
		print "++++ CommentExtractor succesfully done!\n\n\n"

		x = os.system('/home/srijoni/spandan/llvm_build_copy/build/bin/find-class-decls  '+ filename)
		print("Find-class-decls " + str(x))
		#key = input("Hit a key")
		x = 0
		if x != 0 :
			exit(-1)
		print "++++ FindClassDecls succesfully done!\n\n\n"

		x = os.system("python2 ScopeModule.py " + filename)
		if x != 0 :
			exit(-1)
		print "++++ ScopeModule succesfully done!\n\n\n"
		
		os.chdir("Identifier/")
		x = os.system("python2 findclassdecls.py ../" + filename + " ../" + vocab_loc + " ../" + prob_loc)
		if x != 0:
			exit(-1)
		print "++++ Identifier succesfully done!\n\n\n"
		os.chdir("../")

		x = os.system("python2 FinalExcelGeneration.py " + filename + " " + vocab_loc + " " + prob_loc)
		if x != 0:
			exit(-1)
		print "++++ Knowledge base generation done!\n\n\n"

		os.chdir("FeatureDescOp/")
		x = os.system("python2 classify.py ../knowledge_base.csv")
		if x != 0:
			exit(-1)
		print "++++ Feature generation of Description/Operation succesfully done!\n\n\n"
		os.chdir("../")
		
		x = os.system("python2 finalWrite.py " + filename + " knowledge_base.csv")
		if x != 0:
			exit(-1)
		print "++++ Excel written done finally\n\n\n"
	except Exception as e :
		print("Error in running the command " + str(e))
		exit(-1)
	exit(0)
