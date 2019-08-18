import sys
import re
import glob
import os
import shutil

if __name__ == "__main__":
	
	for filename in sys.argv[1:]:
		if os.path.isfile(filename) == True:
			if filename.endswith('.c'):
				fn = filename
				fName1 = str(fn.replace("/" , "_"))
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
					
					x = os.system("python2 CommentExtractor.py " + filename)
					print("CommentExtractor " + str(x))
					#key = input("Hit a key")
					if x != 0 :
						continue
					print "++++ CommentExtractor succesfully done!\n\n\n"

					x = os.system('/home/srijoni/spandan/llvm_build_copy/build/bin/find-class-decls  '+ filename)
					print("Find-class-decls " + str(x))
					#key = input("Hit a key")
					if x != 0 :
						continue
					print "++++ FindClassDecls succesfully done!\n\n\n"
					
					x = os.system("python2 FindAssociations.py " + filename)
					 
					print("FindAssociations " +str(x))
					#key = input("Hit a key")
					if x != 0 :
						continue;
					print "++++ FindAssociations succesfully done!\n\n\n"
					
					try :
						x = os.system("python2 StanfordParsing.py ")
						print("StanfordParsing " + str(x))
						#key = input("Hit a key")
						if x != 0 :
							continue
					except Exception as e:
						print("Error in running StanfordParsing ")
					
					print("Stanford Parsing done\n\n\n")
					
					try:
						x = os.system("python RulesOfCommentAssociation.py " + fName)
						print("RulesOfCommentAssociation " + str(x))
						#key = input("Hit a key	")
						if x != 0 :
							continue
					except Exception as e:
						print("Error in running the rules")
						
					print("Rules of CommentAssociations done\n\n\n")
					
						
					#try :
						#x =  os.system("python2 ValidationOfAFile.py " + filename + " FinalAutomatedPickle" + fName)
						#print("ValidationOfAFile " + str(x))
					#except Exception as e :
						#print("Error in ValidationOfAFile")
								
					
					
				except Exception as e :
						print("Error in running the command " + str(e))
				
				
				#key = input("Hit a key ")
				
				
			

#   for fl in sys.argv[1:]:
#	if fl.endswith('.c') or fl.endswith('.cpp') :
#		print_command(fl)
#   db.close()	





