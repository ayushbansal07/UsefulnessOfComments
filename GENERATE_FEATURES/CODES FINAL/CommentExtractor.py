import sys
import re
import glob
import os

import MySQLdb

# Open database connection
db = MySQLdb.connect("localhost","root","srijoni321","Comments" ,charset='utf8',
                     use_unicode=True )

# prepare a cursor object using cursor() method
cursor = db.cursor()


# Prepare SQL query to INSERT a record into the database.

sql = """ Drop table if exists CommentAnalysis"""
cursor.execute(sql)

cursor.execute("DROP TABLE IF EXISTS AllComments")

# Create table as per requirement
sql = """CREATE TABLE AllComments (
	 id INT NOT NULL AUTO_INCREMENT primary key,
         FILE_NAME  text NOT NULL,
         START_LINE  INT,
         END_LINE INT,  
         COMMENT_TEXT text 
         )"""

cursor.execute(sql)
print ("AllComments is created")

def Insert_In_Db(result) :
	for r in result:
		fname = r[0]
		sline = int(r[1])
		eline = int(r[2])
		text = r[3]
		text = text.replace('\r','')
		sql = "INSERT INTO AllComments(FILE_NAME,START_LINE, END_LINE, COMMENT_TEXT) VALUES (%s , %s , %s , %s)" 
	#sql = "INSERT INTO AllComments(FILE_NAME,START_LINE, END_LINE, COMMENT_TEXT) VALUES ('" + r[0] + "'," + str(r[1]) + "," + str(r[2]) + " , '" + str(text) + "') "
		print (sql)
		try:
   # Execute the SQL command
			cursor.execute(sql,(r[0] , str(r[1]) , str(r[2]) , str(text)))
   # Commit your changes in the database
			db.commit()
		
		except:
			# Rollback in case there is any error
			print ("Error in insertion " + r[0] + " " + str(r[1]) + " " + str(r[2]) + " " + str(text))
			db.rollback()

# disconnect from server
    	

def comment_finder(text):
	pattern = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE).findall(text)
	pattern1 = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)
	l = [(m.start(0), m.end(0)) for m in re.finditer(pattern1, text)]
	print(l)
	print(type(l))
	if len(l) > 0 :
		print(l[0][0])
		
	pos = 0
	fr = []
	to = []
	for item in pattern:
		location = l[pos][0]
		s = text[:location+1]
		lineNo1 = s.count('\n') + 1
		location1 = l[pos][1]
		s = text[:location1 + 1]
		lineNo2 = s.count('\n')
		fr.append(lineNo1)
		to.append(lineNo2)
		print ("lineNo : ",lineNo1 , " to " , lineNo2  , " matched : " , item)
		pos = pos+1
		
	return fr , to , pattern

def print_command(filename):
	codefile = open(filename,'r')
	# commentfile = open(filename+".txt",'w')
	lines=codefile.read()
	# codefile.close()
	#the list of comments
	result = []
	fr , to , list_of_comments = comment_finder(lines)
	pos = 0
	for comment in list_of_comments:
		#print comment[0:2]
		if comment[0:2] == "//":
			comment_to_write = comment[2:]
		else:
			comment_to_write = comment[2:-2]
			
		l = []
		if len(comment_to_write)!=0:
			#commentfile.write(comment_to_write)
			l.append(filename)
			l.append(fr[pos])
			l.append(to[pos])
			l.append(comment_to_write.strip())
			result.append(l)
			
		pos = pos + 1
	print(result)
	Insert_In_Db(result)
        #commentfile.write('\n')
    #commentfile.close()


'''
  The code is to extract comments from the given folder on command line, but it has to be extended to 
  extract comments from folders of folder like DFS.... so that is pending to do... 
'''

if __name__ == "__main__":


#    for dirname in sys.argv[1:]:
#	if os.path.isdir(dirname) == True:
#              files = os.listdir(dirname)
#	      for fl in files:
#	          if fl.endswith('.c') or fl.endswith('.cpp') :
#                     print_command(dirname + "/" + fl)


   for fl in sys.argv[1:]:
	   if fl.endswith('.c') or fl.endswith('.cpp') :
		   print_command(fl)
   db.close()	





