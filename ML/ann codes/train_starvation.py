import tensorflow as tf
import pandas as pd
import numpy as np
import ann
import pickle
import os
import csv
from sklearn.metrics import precision_score, recall_score


df=pd.read_csv('X_train_libpng_cal.csv')
col=df.columns
col_len=len(col)
idx=None
#idx = np.random.permutation(df.shape[0])
#with open('randon_list.pickle','wb') as f:
 #   pickle.dump(idx,f)
idx = np.random.permutation(df.shape[0])
data = df.iloc[idx,:]
data_matrix = pd.DataFrame.as_matrix(data[col])
data_matrix=np.delete(data_matrix, [col_len-1,col_len-2], axis=1)
X = data_matrix
Y = data['Class']
def names_to_onehot(y):
    unique, counts = np.unique(Y, return_counts=True)
    key={}
    i=0
    for u in unique:
        key[str(u)]=i
        i+=1
    print(key)
    one_hot=np.zeros([len(y),len(counts)])
    print(len(y), len(counts))
    j=0
    for i in y:
        one_hot[j,key[str(i)]]=1
        j+=1
    return one_hot,key
def create_dir(path):
    dir_name=path.split('/')
    s=''
    for l in dir_name:
        s=s+l
        
        try:
            os.makedirs(s)
        except:
            pass
            
        s=s+'/'
            
unique, counts = np.unique(Y, return_counts=True)
no_of_classes=(len(counts))
one_hot_y,keys=names_to_onehot(Y)

'''
'x':
'y':
train['x']=X
train['y']=Y
test['x']=X
test['y']=Y
test['x']=X
test['y']=Y optional
'''
train={}
#train['x']=X
#train['y']=one_hot_y
val={}
test={}

l=len(X)
l=int(l*0.20)
train_X=X[0:len(X)-l]
train_Y=one_hot_y[0:len(X)-l]
test['x']=X[len(X)-l:]
test['y']=one_hot_y[len(X)-l:]


test_y=[]
for i in test['y']:
     test_y.append(np.argmax(i))

loss=['softmax']
optimizer=['adam']
result=[]
loss1=['softmax']
layer=[[100,100,100]]
opt='adam'
for l in loss:
    for lay in layer:
        n=train_X.shape[0]
        tmp=[]
        k=10
        s=0
        step=int(n/k)
        i=0
        e=step
        val_acc=[]
        train_acc=[]
        test_acc=[]
        prec=[]
        rec=[]
        while(i<k):
            train={}
            val={}
            x_train1=train_X[0:s:,]
            y_train1=train_Y[0:s:,]
            #print len(x_train1)
            x_train2=train_X[e+1:len(train_X):,]
            y_train2=train_Y[e+1:len(train_X):,]
            
            x_test=train_X[s:e:,]
            y_test=train_Y[s:e:,]
            x_train=np.vstack((x_train1,x_train2))
            y_train=np.vstack((y_train1,y_train2))
            #print len(x_train1),len(x_train2),len(x_train),len(x_test)
            #print len(y_train1),len(y_train2),len(y_train),len(y_test)
            #x_train=pd.DataFrame(x_train)
            train['x']=x_train
            train['y']=y_train
            val['x']=x_test
            val['y']=y_test
            print ('------------------------k=',i,'--------------------')
            model=ann.ann()
            #model=logistic_regression.LRegression()
            model.learning_rate=0.0007
            model.model_restore =False
            model.batch_size=100000
            epoch=2000
            model.epochs=epoch
            model.no_of_features=X.shape[1]
            model.no_of_classes=no_of_classes
            model.working_dir=str(i)
            #model.hidden_layer_list=[100,100,100]
            model.hidden_layer_list=lay
            model.activation_list=['relu','relu','tanh']
            model.loss_type=l
            model.optimizer_type=opt
            model.setup()
            model.train(train,val,epoch)
            res_val=model.test_result
            res_train=model.train_result
            val_acc_res=[d[2] for d in res_val]
            print ('',max(val_acc_res)+1)
            fp=open(str(i)+'/model/'+'checkpoint','w')
            fp.writelines('model_checkpoint_path: "model-'+str(val_acc_res.index(max(val_acc_res))+1)+'"')
            fp.close()
            test_prediction,test_accuracy=model.predict(test)
            test_acc.append(test_accuracy)
            
            p=precision_score(test_y, test_prediction , average = "macro")
            prec.append(p)
    
            r=recall_score(test_y, test_prediction , average = "macro")
            rec.append(r)
            
            
            dir_name=l+'/'+opt
        f=dir_name+'/'+str(i)+'.csv'
        create_dir(dir_name)
        
        fp = open(f, "w")
        fp.write('Training_epoch,Training_loss,Traing accuracy,validation_epoch,validation_loss,validation accuracy')
        fp.write('\n')
        j=0
        while(j<len(res_train)):
            for val in res_train[j]:
                fp.write(str(val))
                fp.write(',')
            for val in res_val[j]:
                fp.write(str(val))
                fp.write(',')
            fp.write('\n')
            j+=1
        fp.close()
        sum_val=0.0;
        sum_train=0.0
        j=len(res_val)-10
        while(j<len(res_val)):
             sum_val+=res_val[j][2]
             sum_train+=res_train[j][2]
             j+=1    
        
        val_acc.append(sum_val/10)
        train_acc.append(sum_train/10)
        
        
        s=e+1
        e=e+step
        if(e>n):
            e=n
        i+=1

        print ("Traing accuracy: ",sum(train_acc)/k,", validation accuracy: ",sum(val_acc)/k,"Test accuracy: ",sum(test_acc)/k,"loss_function: ",l,"optimizer: ",opt ,"precision: ",sum(prec)/k,"recall:",sum(rec)/k)
        tmp.append(sum(train_acc)/k)
        tmp.append(sum(val_acc)/k)
        tmp.append(sum(test_acc)/k)
        tmp.append(l)
        tmp.append(opt)
        tmp.append(sum(prec)/k)
        tmp.append(sum(rec)/k)
        tmp.append(lay)
        result.append(tmp)
        
import csv
fp = open("output.csv", "w")
fp.write('Traing accuracy,validation accuracy,Test accuracy,loss,optimizer,precision,recall,layer')
fp.write('\n')
for row in result:
    for r in row:
        #print r
        fp.write(str(r))
        fp.write(',')
    fp.write('\n')
fp.close()        
                
'''

model=ann.ann()
#model=logistic_regression.LRegression()
model.learning_rate=0.00001
model.model_restore =True
model.batch_size=4096
model.epochs=500
model.no_of_features=X.shape[1]
model.no_of_classes=no_of_classes
model.working_dir='abc'
model.hidden_layer_list=[100,100,100]
model.activation_list=['relu','relu','relu']
#model.loss_type=''
model.setup()
model.train(train)


'''



#model.predict(test)
