
# coding: utf-8

import pandas as pd
import os
from os.path import join as PJOIN
import numpy as np

import sys

DATA_DIR = "DATA/GENERATED/TRAIN/"
#DATA_FILES = ["train_libpng_int.csv", "train_dealii_int.csv", "train_server_int.csv",'handcrafted.csv']
if len(sys.argv) < 3:
    print("Give 1st argument as Name of output file (correlation matrix png), 2nd argument as number of files (n) to concat training data from followed by n file names")
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
        all_x.append(train_x)
    
    all_x = pd.concat(all_x)  
    return all_x

data = get_all_training_data()
print("Length of data ->",len(data))


import seaborn as sns
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(16,6))
sns.heatmap(data.corr(method='pearson'), annot=True, fmt='.4f', 
            cmap=plt.get_cmap('coolwarm'), cbar=False, ax=ax)
ax.set_yticklabels(ax.get_yticklabels(), rotation="horizontal")
#plt.savefig('ANALYSIS/correlation_handcrafted_int.png')
plt.savefig('ANALYSIS/' + OUTPUT_FILE)

print("Successfully Saved plot at - ",'ANALYSIS/'+OUTPUT_FILE)
