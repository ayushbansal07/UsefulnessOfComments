# -*- coding: utf-8 -*-
import re

import sys
import re
import glob
import os

import MySQLdb
import nltk
nltk.data.path.append('/home/srijoni/nltk_data')
from nltk import pos_tag, sent_tokenize, word_tokenize

fname_ = sys.argv[1]
table_dm = "_" + fname_.replace(".", "_")

def words_tok(text) :
	print "text is ", text
	return re.findall("[\O\Θ\Ωa-zA-Z0-9'!#$%&*+-_/=?`{|}~.\"\(\):;.,]+", text, re.UNICODE)
	print "Error not found here"



# Open database connection
dbComment = MySQLdb.connect("localhost","root","srijoni321","Comments" ,charset='utf8',use_unicode=True )

# prepare a cursor object using cursor() method
cursorComment = dbComment.cursor()


dbAST = MySQLdb.connect("localhost","root","srijoni321","test" ,charset='utf8', use_unicode=True )

# prepare a cursor object using cursor() method
cursorAST = dbAST.cursor()


# Create table as per requirement
sql = """ Drop table if exists CommentAssociation"""

cursorComment.execute(sql)


sql = """CREATE TABLE CommentAssociation (
	 id INT NOT NULL AUTO_INCREMENT primary key,
         FILE_NAME  text NOT NULL,
         CommentId INT,
         START_LINE  INT,
         END_LINE INT,  
         COMMENT_TEXT text,
         multiplicity INT default 0,
         NoOfSymbolsMatched INT default 0,
         sameLineSymMatched text,
         compoundLevelNoOfSymbolsMatched INT default 0,
         compoundLineNoString text ,
         compoundLineSymMatched text, 
         compoundLineASTtype text,
         compoundLineDataType text,
         symbol text,
         parent text,
         child text,
         type text,
         data_type text,
         line_begin int,
         line_end int,
         operator text,
         constant text     
         )"""

cursorComment.execute(sql)

sqlInsertCommentAssociation = "Insert into CommentAssociation(FILE_NAME , CommentId , START_LINE, END_LINE, COMMENT_TEXT,multiplicity , NoOfSymbolsMatched , sameLineSymMatched,  compoundLevelNoOfSymbolsMatched ,compoundLineNoString , compoundLineSymMatched , compoundLineASTtype ,compoundLineDataType , symbol, parent , child , type , data_type, line_begin, line_end, operator, constant) values(%s,%s,%s, %s,%s ,%s , %s,  %s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s, %s , %s)"


sameLineMultipleSymbolCheckFlag = False
NoOfSymbolsMatched = 0
multiplicity = 0
scopeFound = False

compoundLevelNoOfSymbolsMatched = 0
compoundLineNoList = list()
compoundLineNoString = ""
sameLineSymMatched = ""
compoundLineSymMatched = ""
sameLineSymList = list()
compoundLineSymList = list()
lineNoOfFirstInclude = 1

compoundLineASTType = list()
compoundLineDataType = list()
compoundLineASTString = ""
compoundLineDataTypeString = ""
ChildTableTraversed = []
ControlList = ['if', 'else', 'for' , 'while', 'do', 'switch' , 'continue' , 'break', 'case']

informativeCommentCheckList = ['copyright','warranty','merchantability','public license', 'program for', 'application for' , 'code for', 'prg for' , 'c code', 'c program']

def formBigrams(Words): 
	bigrams = []
	n = len(Words)
	i = 0
	while True:
		s = Words[i].lower()
		i = i + 1
		if i < n :
			s = s + " " + Words[i].lower()
			bigrams.append(s)
		else :
			break
	return bigrams
	

def checkInformativeComment(sentence) :
	#informativeCommentCheckList
	Words = word_tokenize(sentence)
	for x in Words :
		if x.lower() in informativeCommentCheckList :
			return True
			
	listOfBigrams = formBigrams(Words)
	for x in listOfBigrams :
		if x.lower() in informativeCommentCheckList :
			return True
			
	return False
	

def checkMultiplicityOfComment(CText,tName, CStartLine , CEndLine, checkLineNumber, commentType) :
	global NoOfSymbolsMatched
	global multiplicity
	global compoundLevelNoOfSymbolsMatched
	global compoundLineNoList
	global sameLineSymList
	global compoundLineSymList
	global compoundLineASTType
	global compoundLineDataType
	global ChildTableTraversed
	
	ChildTableTraversed.append(tName)
	print ("called for tName =" + tName)
	Words = word_tokenize(CText)
	WordsLower = word_tokenize(CText.lower())
	print(Words)
	sqlCheck = "select symbol, line_begin, line_end, child, type , data_type from " + tName
	print( sqlCheck   )
	cursorAST.execute(sqlCheck)
	print( "Check" )
	results = cursorAST.fetchall()
	print( "Check again")
	for row in results :
		symbol = row[0]
		lineB = row[1]
		lineE = row[2]
		childTable = row[3]
		if childTable != None and childTable.endswith(table_dm) == False:
			childTable += table_dm
		print "childtable is ", childTable
		ASTtype = row[4]
		datatype = row[5]
		#print (symbol + " " + str(line))
		if symbol != None and ((commentType == "FunctionComment" and ASTtype == "Function") or symbol in Words or (symbol in WordsLower and symbol.lower() in ControlList)) and (lineB != None and (int(lineB) == int(checkLineNumber) or int(lineE) == int(checkLineNumber) )) :
			sameLineSymList.append(symbol)
			print( "Found match of ------- " + symbol)
			print ("Check symbol " + symbol + " line No " + str(lineB))
			if childTable != None and childTable not in ChildTableTraversed:
				checkMultiplicityOfComment(CText, childTable , CStartLine , CEndLine, checkLineNumber, commentType)
		if lineB != None and (int(lineB) == int(checkLineNumber) or int(lineE) == int(checkLineNumber) ):
			print( "Checking on same line")
			multiplicity = multiplicity + 1
		if symbol != None and (symbol in Words or (symbol in WordsLower and symbol.lower() in ControlList)) and int(lineB) != int(checkLineNumber) and int(lineE) != int(checkLineNumber) :
			compoundLineNoList.append(lineB)
			compoundLineSymList.append(symbol)
			compoundLineASTType.append(ASTtype)
			compoundLineDataType.append(datatype)
			if childTable != None and childTable not in ChildTableTraversed:
				checkMultiplicityOfComment(CText, childTable , CStartLine , CEndLine, checkLineNumber, commentType)
			
			print ("Compound Check " + symbol + " line No " + str(lineB))
		if int(lineB) <= int(checkLineNumber) and int(lineE) >= int(checkLineNumber) and (childTable != None) and childTable not in ChildTableTraversed:
			checkMultiplicityOfComment(CText, childTable , CStartLine , CEndLine, checkLineNumber, commentType)
	return multiplicity, sameLineSymList, compoundLineNoList, compoundLineSymList, compoundLineASTType, compoundLineDataType



def makeAssociation(CId, CFileName , CStartLine , CEndLine , CText , tName, checkLineNumber, commentType) :
	global sqlGlobalTable
	global sameLineMultipleSymbolCheckFlag
	global NoOfSymbolsMatched
	global multiplicity
	global compoundLevelNoOfSymbolsMatched
	global compoundLineNoList
	global compoundLineNoString
	global sameLineSymMatched
	global compoundLineSymMatched
	global compoundLineASTType
	global compoundLineDataType
	global scopeFound
	global compoundLineASTString
	global compoundLineDataTypeString
	
	sqlGlobalTable = "select child , parent , symbol , operator, constant , type , data_type, line_begin, line_end from " + tName
	cursorAST.execute(sqlGlobalTable)
	results = cursorAST.fetchall()
	print ("Comment check : " + CText )
	Words = word_tokenize(CText)
	print "no issue with word_tokenize", Words
	for row in results :
		print(row)
		childTable = row[0]
		if childTable != None and childTable.endswith(table_dm) == False:
			childTable += table_dm
		parentTable = row[1]
		symbol = row[2]
		operator = row[3]
		constant = row[4]
		ttype = row[5]
		data_type = row[6]
		line_begin = row[7]
		line_end = row[8]
		if (int(line_begin) <= int(checkLineNumber) and int(line_end) >= int(checkLineNumber)):
			scopeFound = True
			print( sqlInsertCommentAssociation)
			print( str(sameLineMultipleSymbolCheckFlag) )
			#cursorComment.execute("Insert into CommentAssociation(FILE_NAME) values ('" + CFileName + "')")
			if sameLineMultipleSymbolCheckFlag == False :
				multiplicity, sameLineSymList, compoundLineNoList, compoundLineSymList, compoundLineASTType, compoundLineDataType = checkMultiplicityOfComment(CText,tName, CStartLine , CEndLine, checkLineNumber, commentType)
				
				NoOfSymbolsMatched = len(sameLineSymList)
				if commentType == 'FunctionComment' and NoOfSymbolsMatched == 1 :
					sameLineSymList.remove(sameLineSymList[0])
					
					
				compoundLineNoString = ""
				
				for x in compoundLineNoList:
					compoundLineNoString = compoundLineNoString + str(x) + " "
					
				for x in sameLineSymList :
					sameLineSymMatched = sameLineSymMatched + str(x) + " "
					
				for x in compoundLineSymList :
					compoundLineSymMatched = compoundLineSymMatched + str(x) + " "
				
				for x in compoundLineASTType :
					compoundLineASTString = compoundLineASTString + str(x) + " "
					
				for x in compoundLineDataType :
					compoundLineDataTypeString = compoundLineDataTypeString + str(x) + " # "
					
			
				NoOfSymbolsMatched = len(sameLineSymList)
				
				if commentType == 'FunctionComment' and NoOfSymbolsMatched == 1 :
					sameLineSymList.remove(0)
					
				compoundLevelNoOfSymbolsMatched = len(compoundLineNoList)
				sameLineMultipleSymbolCheckFlag = True
			print( "Testing " + str(multiplicity) + " "  + str(NoOfSymbolsMatched) )
			
			cursorComment.execute(sqlInsertCommentAssociation,(CFileName ,str(CId) , str(CStartLine) , str(CEndLine) , CText, str(multiplicity), str(NoOfSymbolsMatched), sameLineSymMatched,  str(compoundLevelNoOfSymbolsMatched), compoundLineNoString,compoundLineSymMatched, compoundLineASTString , compoundLineDataTypeString , symbol, parentTable, childTable, ttype, data_type, str(line_begin) , str(line_end), operator, constant ))
			
			dbComment.commit()
		
		if int(line_begin) <= int(checkLineNumber) and int(line_end) >= int(checkLineNumber) and (childTable != None):
			scopeFound = True
			makeAssociation(CId, CFileName, CStartLine , CEndLine, CText , childTable, checkLineNumber, commentType)

def makeAssociationWithFunction(CId, CFileName , CStartLine , CEndLine , CText , tName) :
	global lineNoOfFirstInclude
	sqlG = "Select child , line_begin, symbol from global" + table_dm + " order by line_begin "
	cursorAST.execute(sqlG)
	results = cursorAST.fetchall()
	sl = int(CStartLine)
	minimum = 500000
	FoundBelowComment = False
	assocLine = 1
	assocTable = "global" + table_dm
	print("Test")
	if checkInformativeComment(CText) == True or CStartLine < lineNoOfFirstInclude:
		print("True")
		
		try :
			cursorComment.execute(sqlInsertCommentAssociation,(CFileName ,str(CId) , str(CStartLine) , str(CEndLine) , CText, "0", "0", "0",  "0", "", "", "", "", "", "", "", "" , "", "0", "0" ,"",""))
			dbComment.commit()
		except Exception as e :
			print("Error in insertion = " + str(e))
		return
		
	for row in results :
		childT = row[0]
		lineB = row[1]
		sym = row[2]
		if sl > lineB and (sl - lineB) < minimum :
			minimum = sl - lineB
			assocLine = lineB
			assocTable = childT
		if sl < lineB :
			FoundBelowComment =  True
			#compoundLineNoList.append(lineB)
			#compoundLineSymList.append(sym)
			#compoundLineASTType.append('Function')
			#compoundLineDataType.append('NULL')
			#cursorComment.execute(sqlInsertCommentAssociation,(CFileName ,str(CId) , str(CStartLine) , str(CEndLine) , CText, "0", "0", "0",  "0", "", "", "", "", sym, "None", "None", "Function" , "NULL", str(CStartLine), str(CStartLine) ,"",""))
			#dbComment.commit()
			print("$$$$$$$$$$$$$$$$$$ Associated with line = " + str(lineB))
			makeAssociation(CId , CFileName ,CStartLine, CEndLine , CText, "global" + table_dm,lineB, "FunctionComment")
			break
			
	if FoundBelowComment == False :
		makeAssociation(CId, CFileName , CStartLine , CStartLine , CText , "global" + table_dm,assocLine, "FunctionComment")
			 
	
	
def makeAssociationOfCommentNotYetAssociated(CId, CFileName , CStartLine , CEndLine , CText) :
	sqlAll = "Show tables";
	cursorAST.execute(sqlAll)
	results = cursorAST.fetchall()
	sl = int(CStartLine)
	minimum = 500000
	minBackWard = 500000
	FoundBelowComment = False
	assocLine = 1
	assocLineBackWard = 1
	for row in results :
		childT = row[0]
		sqlChild = "Select child, symbol, operator, constant, type, data_type, line_begin, line_end from " + childT
		cursorAST.execute(sqlChild)
		entries =  cursorAST.fetchall()
		for entry in entries :
			child = entry[0]
			symbol = entry[1]
			operator = entry[2]
			constant = entry[3]
			ASTtype = entry[4]
			datatype = entry[5]
			line_begin = int(entry[6])
			line_end = int(entry[7])
			if sl <= line_begin :
				if (line_begin - sl) < minimum :
					minimum = line_begin - sl
					assocLine = line_begin
					FoundBelowComment = True
			if sl > line_begin :
				if (sl - line_begin) < minBackWard :
					minBackWard = sl - line_begin
					assocLineBackWard = line_begin
					
					
	if FoundBelowComment == False :
		assocLine = assocLineBackWard
	print("$$$$$$$$$$$$$$$ Associated line number = " + str(assocLine))
	for row in results :
		childT = row[0]
		sqlChild = "Select child, symbol, operator, constant, type, data_type, line_begin, line_end, parent from " + childT
		cursorAST.execute(sqlChild)
		entries =  cursorAST.fetchall()
		for entry in entries :
			child = entry[0]
			symbol = entry[1]
			operator = entry[2]
			constant = entry[3]
			ASTtype = entry[4]
			datatype = entry[5]
			line_begin = int(entry[6])
			line_end = int(entry[7])
			parent = entry[8]
			if line_begin == assocLine :
				try :
					cursorComment.execute(sqlInsertCommentAssociation,(CFileName ,str(CId) , str(CStartLine) , str(CEndLine) , CText, "0", "0", "0",  "0", "", "", "", "", symbol, parent, child, ASTtype , datatype, line_begin, line_end ,operator, constant))
					dbComment.commit()
				except Exception as e :
					print("Error in insertion = " + str(e))
					
					
					
	

sql = "SELECT id , FILE_NAME,START_LINE, END_LINE, COMMENT_TEXT FROM AllComments"


def commentRemover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def FindLineOfFirstInclude(fl) :
	uncmtFile = ""
	with open(fl) as f:
		uncmtFile = commentRemover(f.read())
	i = 1
	for line in uncmtFile.splitlines() :
		Words = re.findall("#include" , line , re.UNICODE)
		if len(Words) != 0 :
			return i
		i = i + 1
	return 1

if __name__ == "__main__":
	try:
	
	# Execute the SQL command
		for fl in sys.argv[1:]:
			if fl.endswith('.c') or fl.endswith('.cpp') :
				lineNoOfFirstInclude = FindLineOfFirstInclude(fl)
		print("First Include line No = " + str(lineNoOfFirstInclude))
		cursorComment.execute(sql)
		# Fetch all the rows in a list of lists.
		results = cursorComment.fetchall()
		print("+++ Results:", results)
		for row in results:
			CId = row[0]
			CFileName = row[1]
			CStartLine = row[2]
			CEndLine = row[3]
			CText = row[4]
			scopeFound = False
			sameLineMultipleSymbolCheckFlag = False
			NoOfSymbolsMatched = 0
			multiplicity = 0
			compoundLevelNoOfSymbolsMatched = 0
			compoundLineNoList = []
			compoundLineNoString = ""
			sameLineSymMatched = ""
			compoundLineSymMatched = ""
			sameLineSymList = []
			compoundLineSymList = []
			compoundLineASTType = []
			compoundLineDataType = []
			ChildTableTraversed = []
			compoundLineASTString = ""
			compoundLineDataTypeString = ""
			print "Reaching here!"
			makeAssociation(CId, CFileName , CStartLine , CEndLine , CText , 'global' + table_dm, CStartLine, 'GeneralComment')
			print("Scope Found == " + str(scopeFound))
			if scopeFound == False :
				makeAssociationWithFunction(CId, CFileName , CStartLine, CEndLine, CText, 'global' + table_dm)
			
		
		
			if scopeFound == True and multiplicity == 0 and compoundLevelNoOfSymbolsMatched == 0 and NoOfSymbolsMatched == 0 :
				makeAssociationOfCommentNotYetAssociated(CId, CFileName , CStartLine, CEndLine, CText)
		
			# key = input("Hit a key to check individual comment " )
		
		#POSTagging(CId , CText)
		#print "Comment --- " + CText
		#Words = word_tokenize(CText)
		#InsertIntoDB(CId , Words)
		# Now print fetched result
		#print "CId=%d,CText=%s" % (CId, CText)
	except Exception as e:
		print( "Error: unable to fecth data " + str(e))

# disconnect from server
	dbComment.close()
	dbAST.close()







