import os
import csv
import json
import sys

def writeError(fpath):
	f = open("errorfiles.txt", "a+")
	f.write(fpath + "\n")
    	f.close()

def visitor(filters, dirname, names):
        mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
        for name in mynames:
                fpath = os.path.join(dirname, name)
                if not os.path.isdir(fpath):
                        print "Filename", fpath
                        try:
				os.system("python2 filterFile.py " + fpath)
                            	x = 0
				x = os.system('/home/srijoni/spandan/llvm_build_copy/build/bin/find-class-decls  '+ fpath)
				if x != 0:
					writeError(fpath)
                                print "++++ FindClassDecls succesfully done!\n\n"
                        except Exception as e:
				writeError(fpath)
				

if __name__ == "__main__":
        if len(sys.argv) != 2:
                print("Give 1 argument, the project location")
                exit(-1)
        filters = [".c"]
        os.path.walk(sys.argv[1], visitor, filters)

