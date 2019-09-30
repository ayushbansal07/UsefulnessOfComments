# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from os.path import join as PJOIN
import sys

if len(sys.argv)!=3:
    print("Give 2 Arguments - 1) Annonations file name, 2) Project Name")
    exit(-1)

FILE_NAME = sys.argv[1]
PROJECT_NAME = sys.argv[2]
FILE_PATH = PJOIN("DATA","ANNOTATED",FILE_NAME)
OUTPUT_FILE_PATH = PJOIN("DATA","GENERATED",FILE_NAME)
MAP = {'U':'U', 'PU':'P', 'NU':'N'}
THRESHOLD = 10

# c is a vector of size 31 [comment text, C1, C2, ......., C30]
def get_label(c):
    #IF C18 OR C19 OR C20  OR  C21  OR C22 OR C28 OR C29 THEN  U
    if c[18] or c[19] or c[20] or c[21] or c[22] or c[28] or c[29]:
        return 'U'
    #IF C9 AND C3 THEN U
    if c[9] and c[3]:
        return 'U'
    #IF C11 AND C3 THEN U
    if c[11] and c[3]:
        return 'U'
    #IF (C25 OR C23 OR C26 OR C27 ) AND C3 THEN U
    if (c[25] or c[23] or c[26] or c[27]) and c[3]:
        return 'U'
    #IF (C25 OR C23 OR C26 OR C27) AND C4 AND (C9  OR C11) THEN U
    if (c[25] or c[23] or c[26] or c[27]) and c[4] and (c[9] or c[11]):
        return 'U'
    #IF C10 AND C15  AND C3 THEN U
    if c[10] and c[15] and c[3]:
        return 'U'
    #IF C8 AND C15  AND C3 THEN U
    if c[8] and c[15] and c[3]:
        return 'U'
    #IF (C18 OR C19 OR C20 OR C21) AND C17 THEN U
    if (c[18] or c[19] or c[20] or c[21]) and c[17]:
        return 'U'
    #Low Problem Domain AND Low Scope AND Concepts don't match Symbols = U
    if c[10] and c[15] and c[3]:
        return 'U'
    #Low Problem Domain AND Low Scope AND Concepts Partially Match = U
    if c[10] and c[15] and c[4]:
        return 'U'
    
    #IF C9 AND (C4 OR C5) THEN PU
    if c[9] and (c[4] or c[5]):
        return 'PU'
    #IF C11 AND (C4  OR C5) THEN PU
    if c[11] and (c[4] or c[5]):
        return 'PU'
    #IF C10 AND C14  AND C3 THEN PU
    if c[1] and c[14] and c[3]:
        return 'PU'
    #IF C8 AND C14  AND C3 THEN PU
    if c[8] and c[14] and c[3]:
        return 'PU'
    #IF C17 AND NOT (C18 OR C19 OR C20 OR C21)  THEN PU
    if c[17] and not((c[18] or c[19] or c[20] or c[21])):
        return 'PU'
    #Low  Problem Domain AND Concepts Partially Match = PU
    if c[10] and c[4]:
        return 'PU'
    #Low Program Domain AND Concepts Partially Match = PU
    if c[8] and c[4]:
        return 'PU'
    
    #IF C12 OR C16 THEN  NU
    if c[12] or c[16]:
        return 'NU'
    #IF (C8 OR C9)  AND C1 THEN NU
    if (c[8] or c[9]) and c[1]:
        return 'NU'
    #IF (C10 OR C11) AND C1 THEN NU
    if (c[10] or c[11]) and c[1]:
        return 'NU'
    #IF C10 AND C15  AND C1 THEN U
    if c[10] and c[15] and c[1]:
        return 'NU'
    #IF C8 AND C15  AND C1 THEN U
    if c[8] and c[15] and c[1]:
        return 'NU'

    return 'NU'
    



if FILE_PATH[-3:] == 'csv':
    exl_file = pd.read_csv(FILE_PATH,delimiter='\t')
else:
    exl_file = pd.read_excel(FILE_PATH)

exl_np = np.array(exl_file)
classes = exl_np[:,[1]+list(range(16,46))]
#print(classes[0])

for j, c in enumerate(classes):
    for i in range(1,31):
        try:
            if c[i] != c[i]:
                c[i] = False
            elif int(c[i]) == 1:
                c[i] = True
            else:
                c[i] = False
        except:
            print(j, i)

labels = []
for c in classes:
    labels.append(MAP[get_label(c)])

exl_file['Calculated Score'] = labels


if FILE_PATH[-3:] == 'csv':
    exl_file.to_csv(OUTPUT_FILE_PATH,index=False)
else:
    exl_file.to_excel(OUTPUT_FILE_PATH, index=False)


print("Successfully Written Calculated Labels file at - ",OUTPUT_FILE_PATH)


#Analysis - Finding examples where Intuitive Score does not match calculated score.
intuitive_labels = exl_np[:,-1]
lables_np = np.array(labels)

num_nan = np.sum(np.array([x !=x for x in intuitive_labels]))

print("Fraction of examples where Intuitive Label = Calculated Label -> ",sum(lables_np == intuitive_labels)/(len(lables_np) - num_nan), "Total Examples ->", (len(lables_np) - num_nan))


losses = {}
def get_hash(classes):
    hsh = []
    for i, c in enumerate(classes):
        if c == True:
            hsh.append(i+1)
    return str(hsh)

for i in range(len(intuitive_labels)):
    if intuitive_labels[i]!=intuitive_labels[i]:
        continue
    li = intuitive_labels[i][0]
    lc = lables_np[i]
    if li not in losses:
        losses[li] = {}
    if lc not in losses[li]:
        losses[li][lc] = {}
    if li==lc:
        continue
    myhash = get_hash(classes[i][1:])
    if myhash not in losses[li][lc]:
        losses[li][lc][myhash] = 0
    losses[li][lc][myhash] += 1

alls = []
for li, v1 in losses.items():
    for lc, v2 in v1.items():
        curr = 0
        tops_curr = None
        for  myhash, ct in v2.items():
            alls.append([li,lc,myhash,ct])

alls = sorted(alls,key=lambda x:(x[3],x[0],x[1]),reverse=True)
# print("Inutinitive Label | Calculated Label | Classes which have 1 | Number of such mismatch")
# print(alls)

RULE_DIFFS_COUNTS_FILE = 'DATA/ANNOTATED/rule_diffs/'+PROJECT_NAME+".csv"

import csv
with open(RULE_DIFFS_COUNTS_FILE,'w') as f:
    writer = csv.writer(f)
    writer.writerow(["Intuitive Label","Calculated Label", "Classes which have 1 marked","Number of Mismatches", "Name"])
    for i, row in enumerate(alls):
        if row[3] < THRESHOLD:
            break
        writer.writerow(row + ["Case "+str(i+1)])

print("Successfully Written Rule Diff counts file at - ",RULE_DIFFS_COUNTS_FILE)



alls_map = {}
for i, row in enumerate(alls):
    if row[3] < THRESHOLD:
        break
    alls_map[(row[0],row[1],row[2])] = i+1

diff_names = []
diffs_map = {}
for i in range(len(intuitive_labels)):
    if intuitive_labels[i]!=intuitive_labels[i]:
        diff_names.append(None)
        continue
    li = intuitive_labels[i][0]
    lc = lables_np[i]
    myhash = get_hash(classes[i][1:])
    if (li, lc, myhash) not in alls_map:
        diff_names.append(None)
        continue
    diff_names.append("Case " + str(alls_map[(li, lc, myhash)]))
    if alls_map[(li, lc, myhash)] not in diffs_map:
        diffs_map[alls_map[(li, lc, myhash)]] = []
    diffs_map[alls_map[(li, lc, myhash)]].append(i)


exl_file['Mismatch Case'] = diff_names

DIFFS_FILE = FILE_NAME
if DIFFS_FILE[-3:] == 'csv':
    DIFFS_FILE = DIFFS_FILE[:-3] + 'xlsx'


RULE_DIFFS_FILE = "DATA/ANNOTATED/rule_diffs/"+DIFFS_FILE
writer = pd.ExcelWriter(RULE_DIFFS_FILE, engine = 'xlsxwriter')

exl_file.to_excel(writer,index=False)

for k,v in diffs_map.items():
    df = pd.DataFrame(columns=exl_file.columns)
    for i, j in enumerate(v):
        df.loc[i] = exl_file.loc[j]
    df.to_excel(writer,index=False,sheet_name='Case '+str(k))

writer.save()
writer.close()
print("Successfully Written Rule diffs file at - ",RULE_DIFFS_FILE)
print("Program Completed Successfully!!")
