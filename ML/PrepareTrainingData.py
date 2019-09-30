# coding: utf-8
import os
import pandas as pd
import numpy as np
from os.path import join as PJOIN
import sys

if len(sys.argv)!=5:
    print("Give 4 arguments - 1) Features Directory, 2) Annotations File (Calculated), 3) Project Name, 4) Which label to use (cal, int or calint)")
    print("Note: The 4th argument can be only one of these 3 -> a) cal (use calculated labels), b) int (use intuitive labels),\
        c) calint (use calculated labels but only for examples for which intuitive are present)")
    exit(-1)

if sys.argv[4] not in ["cal","int","calint"]:
    print("Invalid 4th Argument, See help")
    exit(-1)

#FEATURES_DIR = "DATA/CSV/dealii/"
FEATURES_DIR = sys.argv[1]
#ANNOTATIONS_FILE = "DATA/GENERATED/comments_dealii_all.xlsx"
ANNOTATIONS_FILE = sys.argv[2]
PROJECT_NAME = sys.argv[3]
OUTPUT_DIR = "DATA/GENERATED/TRAIN/"
# sys.argv[4] can be only one of these 3 -> 1) cal (use calculated labels), 2) int (use intuitive labels),
# 3) calint (use calculated labels but only for examples for which intuitive are present)
OUTPUT_SUFFIX = "_" + sys.argv[4]

OUTPUT_FILENAME = "train_" + PROJECT_NAME + OUTPUT_SUFFIX + ".csv"
ANNOTATIONS = {'N':1,'P':2,'U':3}

if ANNOTATIONS_FILE[-3:] == 'csv':
    annotations_file = pd.read_csv(ANNOTATIONS_FILE)
else:
    annotations_file = pd.read_excel(ANNOTATIONS_FILE)

annotations_np = np.array(annotations_file)

annotations_map = {}
for anno in annotations_np:
    if anno[0] not in annotations_map:
        annotations_map[anno[0]] = []
    annotations_map[anno[0]].append(anno[1:])

all_files = []
for file in os.listdir(FEATURES_DIR):
    if not file.endswith("train.csv"):
        continue
    if not PROJECT_NAME in file:
        continue
    fName = file[file.find(PROJECT_NAME) + 1 + len(PROJECT_NAME) : -10]
    #print(fName)
    fName = fName.replace("_","/")
    #print(fName)
    all_files.append(fName)

not_found = []
found = []
CODENAME_TO_COMMENTSFILENAME = {}
for comments_file, annos in annotations_map.items():
    fName = comments_file[comments_file.find(PROJECT_NAME) + len(PROJECT_NAME) +1:]
    fName = fName.replace("_","/")
    if fName[:7] == 'mariadb':
        fName = fName[8:]
    CODENAME_TO_COMMENTSFILENAME[fName] = comments_file
    #print(fName)
    if fName not in all_files:
        not_found.append(fName)
    else:
        found.append(fName)
print("========Not Found=========")
print(not_found)
print("========FOUND=======")
print(found)

print("Data Prepapration Start!")

X = []
Y = []
for file in os.listdir(FEATURES_DIR):
    if not file.endswith("train.csv"):
        continue
    if not PROJECT_NAME in file:
        continue
    fName = file[file.find(PROJECT_NAME) + 1 + len(PROJECT_NAME) : -10]
    fName = fName.replace("_","/")
    if fName not in found:
        print("LEFT: ",fName)
        continue
    #print(fName)
    anno_data = annotations_map[CODENAME_TO_COMMENTSFILENAME[fName]]
    features_file = pd.read_csv(PJOIN(FEATURES_DIR,file),header=None,encoding="ISO-8859–1")
    features_np = np.array(features_file)
    features_map = {}
    for feat in features_np:
        if len(feat[2:]) > 12:
            print("ERROR: Length of features greater than 12")
            print(feat)
        features_map[feat[1]] = feat[2:14]
    for comments_data in anno_data:
        if comments_data[0] not in features_map:
            print("Comment NOT FOUND:",comments_data[0])
            continue
        features = features_map[comments_data[0]]
        labels_intuitive = comments_data[-2]
        labels_calculated = comments_data[-1] 
        if OUTPUT_SUFFIX == '_cal':
            label_used = labels_calculated
            label_compared = labels_calculated
        elif OUTPUT_SUFFIX == '_int':
            label_used = labels_intuitive
            label_compared = labels_intuitive
        elif OUTPUT_SUFFIX == '_calint':
            label_used = labels_calculated
            label_compared = labels_intuitive
        if label_compared != label_compared:
            continue
        X.append(features)
        Y.append(ANNOTATIONS[label_used[0]])

for x in X:
    if len(x) != len(X[0]):
        print("Length of feature not appropriate - ",len(x))


print("Number of Training examples generated - ",len(X))

import csv
with open(PJOIN(OUTPUT_DIR,"X_"+OUTPUT_FILENAME),'w') as f:
    writer = csv.writer(f)
    for x in X:
        writer.writerow(x)
print("Successfully Written X Train file at - ",PJOIN(OUTPUT_DIR,"X_"+OUTPUT_FILENAME))
with open(PJOIN(OUTPUT_DIR,"Y_"+OUTPUT_FILENAME),'w') as f:
    writer = csv.writer(f)
    for y in Y:
        writer.writerow([y])
print("Successfully Written Y Train file at - ",PJOIN(OUTPUT_DIR,"Y_"+OUTPUT_FILENAME))
print("Program Completed Successfully!!")
