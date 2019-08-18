# Reference : https://scikit-learn.org/stable/modules/tree.html

from sklearn import tree
import csv
import pickle
from sklearn import cross_validation
from sklearn.cross_validation import cross_val_score
from sklearn import svm

def readCSV(fname):
	f = open(fname, 'r')
	r = csv.reader(f)
	out = []
	for each in r:
		now = []
		for x in range(2, len(each)):
			now.append(float(x))
		out.append(now)
	f.close()
	return out

def loadX(fname):
	data = readCSV(fname)
	return data
	
def loadY(fname):	
	f = open(fname, 'r')
        r = csv.reader(f)
        Y = []
        for each in r:
      		Y.append(int(each[0]))          
        f.close()
	return Y


def saveClassifier(clf, model_name):
	pickle.dump(clf, open(model_name, 'wb'))

def exportClassifier(model_name):
	return pickle.load(model_name)

def runDecisionTree(x, y):
	print "Running Decision Tree...."	
	x_train, x_test, y_train, y_test = cross_validation.train_test_split(x, y, test_size=0.1, random_state=0)
	depth = []
	for i in range(3,20):
	    clf = tree.DecisionTreeClassifier(max_depth=i)
	    scores = cross_val_score(estimator=clf, X=x, y=y, cv=9, n_jobs=4)
	    depth.append((i,scores.mean()))
	print(depth)


def runSVM(x, y):
	print "Running SVM...."
	x_train, x_test, y_train, y_test = cross_validation.train_test_split(x, y, test_size=0.1, random_state=0)
	clf = svm.SVC(kernel='linear', C=1).fit(x_train, y_train)
	print clf.score(x_test, y_test)


import sys
if len(sys.argv) != 3:
	print "Give two arguments, the locations to the X training data and Y data"
	exit(-1)

X = loadX(sys.argv[1])  # 2d list
Y = loadY(sys.argv[2])
print len(X), len(Y)

runDecisionTree(X, Y)
runSVM(X, Y)
