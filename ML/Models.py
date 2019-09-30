# coding: utf-8
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn import cross_validation
from sklearn import tree
from sklearn.cross_validation import cross_val_score
from os.path import join as PJOIN
import os
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_predict
from sklearn.cluster import KMeans
import sys

DATA_DIR = "DATA/GENERATED/TRAIN/"
#DATA_FILES = ["train_libpng_calint.csv", "train_dealii_calint.csv", "train_server_calint.csv", "handcrafted.csv"]
if len(sys.argv) < 3:
    print("Give 1st argument as Name of output file, 2nd argument as number of files (n) to concat training data from followed by n file names")
    exit(-1)
OUTPUT_FILE = sys.argv[1]
DATA_FILES = []
for i in range(int(sys.argv[2])):
    DATA_FILES.append(sys.argv[i+3])

def get_all_training_data():
    all_files = []
    if DATA_FILES[0] == 'all':
        for file in os.listdir(DATA_DIR):
            if file[:2] == 'X_':
                all_files.append(file[2:])
    else:
        all_files = DATA_FILES
    
    all_x = []
    all_y = []
    for file in all_files:
        train_x = pd.read_csv(PJOIN(DATA_DIR,"X_"+file),header=None)
        all_x.append(np.array(train_x))
        train_y = pd.read_csv(PJOIN(DATA_DIR,"Y_"+file),header=None)
        all_y.append(train_y)
    
    all_x = np.concatenate(all_x)
    all_y = np.concatenate(all_y)
    #print(all_x.shape,all_y.shape)
    all_y = all_y.reshape(all_y.shape[0])    
    return all_x, all_y

def normalize_data(x):
    return (x - np.mean(x,axis=0))/np.std(x,axis=0)

train_x, train_y = get_all_training_data()
train_x = normalize_data(train_x)
print("Shape of TrainX, TrainY ->",train_x.shape, train_y.shape)
print("Num Label 1, 2 and 3 ->",np.sum(train_y==1), np.sum(train_y==2), np.sum(train_y==3))


def runSVM_CV(x, y):
    print("Running SVM....")
    perm = np.random.permutation(len(x))
    x = x[perm]
    y = y[perm]
    clf = svm.SVC(kernel='linear', C=1,max_iter=1000000)
    return cross_val_predict(clf, x, y,cv=5),y 

# preds, test = runSVM_CV(train_x, train_y)
# print("SVM: ")
# print("Precision Recall FScore")
# print(precision_recall_fscore_support(test, preds))
# print("Accuracy: ")
# print(accuracy_score(test,preds))
# print("Num Label 1, 2, 3 in Test")
# print(np.sum(test==1), np.sum(test==2), np.sum(test==3))
# print("Num Label 1, 2, 3 in Predictions")
# print(np.sum(preds==1), np.sum(preds==2), np.sum(preds==3))
# print("------------------------------------------------------------------------------")

def run_ann_CV(x,y):
    print("Running ANN....")
    perm = np.random.permutation(len(x))
    x = x[perm]
    y = y[perm]
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                        hidden_layer_sizes=(20, 8), random_state=1)
    return cross_val_predict(clf, x, y,cv=5),y 

# preds, test = run_ann_CV(train_x, train_y)
# print("ANN: ")
# print("Precision Recall FScore")
# print(precision_recall_fscore_support(test, preds))
# print("Accuracy: ")
# print(accuracy_score(test,preds))
# print("Num Label 1, 2, 3 in Test")
# print(np.sum(test==1), np.sum(test==2), np.sum(test==3))
# print("Num Label 1, 2, 3 in Predictions")
# print(np.sum(preds==1), np.sum(preds==2), np.sum(preds==3))
# print("------------------------------------------------------------------------------")


preds_svm, test_svm = runSVM_CV(train_x, train_y)
pr_svm = precision_recall_fscore_support(test_svm, preds_svm)
mpr_svm = precision_recall_fscore_support(test_svm, preds_svm,average='micro')
preds_ann, test_ann = run_ann_CV(train_x, train_y)
pr_ann = precision_recall_fscore_support(test_ann, preds_ann)
mpr_ann = precision_recall_fscore_support(test_ann, preds_ann,average='micro')

import csv
#OUTPUT_FILE_NAME = "ANALYSIS/summary_cal_handcrafted.csv"
OUTPUT_FILE_NAME = "ANALYSIS/" + OUTPUT_FILE
with open(OUTPUT_FILE_NAME,'w') as f:
    writer = csv.writer(f)
    writer.writerow(["Feature","SVM","ANN"])
    writer.writerow([])
    writer.writerow(["Num True Label 1",np.sum(test_svm==1),np.sum(test_ann==1)])
    writer.writerow(["Num True Label 2",np.sum(test_svm==2),np.sum(test_ann==2)])
    writer.writerow(["Num True Label 3",np.sum(test_svm==3),np.sum(test_ann==3)])
    writer.writerow([])
    writer.writerow(["Num Predicted Label 1",np.sum(preds_svm==1),np.sum(preds_ann==1)])
    writer.writerow(["Num Predicted Label 2",np.sum(preds_svm==2),np.sum(preds_ann==2)])
    writer.writerow(["Num Predicted Label 3",np.sum(preds_svm==3),np.sum(preds_ann==3)])
    writer.writerow([])
    writer.writerow(["Accuracy",accuracy_score(test_svm,preds_svm),accuracy_score(test_ann, preds_ann)])
    writer.writerow(["Micro Precision",mpr_svm[0],mpr_ann[0]])
    writer.writerow(["Micro Recall",mpr_svm[1],mpr_ann[1]])    
    writer.writerow(["Micro F1",mpr_svm[2],mpr_ann[2]])  
    writer.writerow([])
    writer.writerow(["Precision for Label 1",pr_svm[0][0],pr_ann[0][0]])
    writer.writerow(["Precision for Label 2",pr_svm[1][0],pr_ann[1][0]])    
    writer.writerow(["Precision for Label 3",pr_svm[2][0],pr_ann[2][0]])    
    writer.writerow([])
    writer.writerow(["Recall for Label 1",pr_svm[0][1],pr_ann[0][1]])
    writer.writerow(["Recall for Label 2",pr_svm[1][1],pr_ann[1][1]])    
    writer.writerow(["Recall for Label 3",pr_svm[2][1],pr_ann[2][1]])
    writer.writerow([])
    writer.writerow(["F1 for Label 1",pr_svm[0][2],pr_ann[0][2]])
    writer.writerow(["F1 for Label 2",pr_svm[1][2],pr_ann[1][2]])    
    writer.writerow(["F1 for Label 3",pr_svm[2][2],pr_ann[2][2]])

print("Analysis file for SVM and ANN Generated at - ",OUTPUT_FILE_NAME)




#Clustering
kmeans = KMeans(n_clusters=4, random_state=0).fit(train_x)
lbls = kmeans.labels_
print("Clustering Labels Counts")
print(np.sum(lbls==0), np.sum(lbls==1), np.sum(lbls==2), np.sum(lbls==3))

