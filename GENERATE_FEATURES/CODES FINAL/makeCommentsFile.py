import sys
import re
import glob
import os
import shutil
import MySQLdb
import csv

# Returns comments from the database
def getComments():
	# Open database connection
	db = MySQLdb.connect("localhost","root","srijoni321","Comments" ,charset='utf8',
	                     use_unicode=True )

	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	# fetch all comments from the database
	sql = """ select * from AllComments; """
	cursor.execute(sql)
	comments = cursor.fetchall()
	return comments

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Give 1 argument: filename")
		exit(-1)
	
	filename = sys.argv[1]
	
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
		x = os.system("python2 CommentExtractor.py " + filename)
		print("CommentExtractor " + str(x))
		#key = input("Hit a key")
		if x != 0 :
			exit(-1)
		print "++++ CommentExtractor succesfully done!\n\n\n"
		
		results = getComments()
		with open("/data/Harsha/Complete Dump/ParserCheck/commentsfile.csv", 'a+') as csvfile:
    			spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    			for each in results:		
				spamwriter.writerow([each[4], ""])

	except Exception as e :
		print("Error in running the command " + str(e))
		exit(-1)
	exit(0)
