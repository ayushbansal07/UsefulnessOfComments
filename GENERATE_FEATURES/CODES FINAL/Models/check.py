# Reference : https://scikit-learn.org/stable/modules/tree.html

from sklearn import tree
import csv
import pickle
from sklearn import model_selection
# from sklearn.model_selection import cross_validation
# from sklearn.cross_validation import cross_val_score
from sklearn import svm
from sklearn.metrics import precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier

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

def mywriteCSV(X, Y):
	output = []
	for i in range(len(X)):
		now = X[i]
		now.append(Y[i])
		output.append(now)

	f = open("clubbed_data.csv", 'w')
	writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
	for each in output:
		writer.writerow(each)
	f.close()

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
	
	clf = tree.DecisionTreeClassifier(max_depth=20)
	clf.fit(x_train, y_train)	
	y_pred = clf.predict(x_test)
	print "Terms:", precision_recall_fscore_support(y_test, y_pred, average='weighted')	
	
	depth = []
	for i in range(3,20):
		clf = tree.DecisionTreeClassifier(max_depth=i)
		scores = cross_val_score(estimator=clf, X=x, y=y, cv=9, n_jobs=4)	
		depth.append((i,scores.mean()))
	print "Accuracy:", (depth)

from sklearn.model_selection import KFold
	
def check(X, Y):

	print "Running Decision Tree...."	

	x, x1, y, y1 = model_selection.train_test_split(X, Y, test_size=0.1, random_state=0)

	kf = KFold(n_splits=10)	
	
	all_cross = []
	all_test = []
	for train_index, test_index in kf.split(x):
		x_train = []
		x_test = []
		y_train = []
		y_test = []
		for each in train_index:
			x_train.append(x[each])
			y_train.append(y[each])
		for each in test_index:
			x_test.append(x[each])
			y_test.append(y[each])
		clf = MLPClassifier(hidden_layer_sizes=(15,15,3), random_state=1, max_iter=10000, warm_start=True)
		clf = clf.fit(x_train, y_train)
		y_pred = clf.predict(x_test)
		cross_score_now = precision_recall_fscore_support(y_test, y_pred, average='weighted')
		print y_test
		print y_pred
		print confusion_matrix(y_test, y_pred)		

		y_pred = clf.predict(x1)
		test_score_now = precision_recall_fscore_support(y1, y_pred, average='weighted')
		print confusion_matrix(y1, y_pred)

		all_cross.append(cross_score_now)
		all_test.append(test_score_now)
		
	
	results_cross = [0.0, 0.0, 0.0]
	for i in range(len(all_cross)):
		for j in range(3):
			results_cross[j] += all_cross[i][j]
	
	results_test = [0.0, 0.0, 0.0]
	for i in range(len(all_test)):
		for j in range(3):
			results_test[j] += all_test[i][j]
	
	for j in range(3):
		results_cross[j] /= float(len(all_cross))
		results_test[j] /= float(len(all_test))

	print "Cross:", results_cross
	print "Test:", results_test

def runNormalDecidionTree(x, y):
	print "Running Decision Tree...."	
	x_train = x[:900]
	y_train = y[:900]
	x_test = x[900:]
	y_test = y[900:]
	depth = []
	for i in range(3,20):
		clf = tree.DecisionTreeClassifier(max_depth=i)	
		clf.fit(x_train, y_train)			
		depth.append((i,clf.score(x_test, y_test)))
	print "Accuracy:", (depth)

def runSVM(x, y):
	print "Running SVM...."
	x_train, x_test, y_train, y_test = cross_validation.train_test_split(x, y, test_size=0.1, random_state=0)
	clf = svm.SVC(kernel='linear', C=1).fit(x_train, y_train)
	print "Accuracy", clf.score(x_test, y_test)
	y_pred = clf.predict(x_test)
	print "Terms:", precision_recall_fscore_support(y_test, y_pred, average='weighted')
	
def runRandomForest(x, y):
	print "Running Random Forest....."
	clf = RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)
	clf.fit(x, y)
	scores = cross_val_score(estimator=clf, X=x, y=y, cv=9, n_jobs=4)
	# y_pred = clf.predict(x_test)
	# print "Terms:", precision_recall_fscore_support(y_test, y_pred, average='weighted')
	print "Accuracy:", scores.mean()	

import sys
if len(sys.argv) != 3:
	print "Give two arguments, the locations to the X training data and Y data"
	exit(-1)

X = loadX(sys.argv[1])  # 2d list
Y = loadY(sys.argv[2])
print Y
print len(X), len(Y)

z = [1]*121
Y.extend(z)
print len(X), len(Y)

# X = X[-121:]
# Y = z

# runNormalDecidionTree(X, Y)
# runDecisionTree(X, Y)
# runSVM(X, Y)
# runRandomForest(X, Y)

# mywriteCSV(X,Y)

import random

def myRandomShuffle(X, Y):
	for i in range(len(X)):
		j = random.randrange(i, len(X))
		temp = X[i]
		X[i] = X[j]
		X[j] = temp

		temp = Y[i]
		Y[i] = Y[j]
		Y[j] = temp
		print type(X[i][0]), type(Y[i])
	return (X,Y)

(X, Y) = myRandomShuffle(X, Y)
check(X, Y)
