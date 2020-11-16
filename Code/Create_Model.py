#import libraries
import ast
import numpy as np
import argparse
from numpy import array
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Masking
import math
import csv
import statistics
parser = argparse.ArgumentParser(description='Model creation parameters')
parser.add_argument('--DNA',help="Please enter the model dna", default='[[80, 2, 0, 0, 9], [169, 2, 1, 0, 2], [41, 3, 0, 0, 9], [54, 4, 1, 0, 0], [], [4]]')
parser.add_argument('--Samples',help="Please enter the number of training samples", default='20')
parser.add_argument('--ValSamples',help="Please enter the number of validation samples", default='20')
parser.add_argument('--LossFunct',help="Please enter the loss function", default='mse')
parser.add_argument('--TrackLength',help="Please enter the track number", default='3')
args = parser.parse_args()
#setting main learning parameters
gaps=1
features=4
tr_samples=int(args.Samples)
val_samples=int(args.ValSamples)
TrackLength=int(args.TrackLength)
TrainFile='/eos/experiment/ship/user/ffedship/CHARM/Train_Material/CHARM_NORM_TRAIN_1.csv'
ValFile='/eos/experiment/ship/user/ffedship/CHARM/Train_Material/CHARM_NORM_VAL.csv'
DNA=ast.literal_eval(args.DNA)
Layers=0
NewDNA=[]

for gene in DNA:
    if len(gene)==5:
        NewDNA.append(gene)
    if len(gene)==1:
        Layers+=1
print(Layers)
print(NewDNA)
exit()
_=0
##############This function gives training data to LSTM model for training################################
###Samples - number of samples per each set
###Start PID - Choose PID at which first for a given track in the sample observed 0-28
###Number of steps
###Varuiable: x,y(it was implemented so we don't have to write the same function 4 times)
def GiveData(StSample, FinSample, TrackLength, Variable,file):
  if Variable=='x':
      Var=3
  if Variable=='y':
      Var=4
  if Variable=='tx':
      Var=5
  if Variable=='ty':
      Var=6
  x=list()
  xO=list()

  with open(file) as csv_train_file:
    csv_reader_train = csv.reader(csv_train_file, delimiter=',')
    seq_x=list()
    seq_x0=list()
    SEQ=0
    for SEQ in range(StSample,FinSample):
      SUB_SEQ=0
      seq_x=[]
      seq_x0=[]
      for SUB_SEQ in range(0,TrackLength):
        for row in csv_reader_train:
            if row[0]!='SEQ':
              if SEQ==int(row[0]):
               if TrackLength==int(row[1]):
                   if SUB_SEQ==int(row[2]) and SUB_SEQ<TrackLength-1:
                      seq_x.append(float(row[Var]))
                      SUB_SEQ+=1
                   if SUB_SEQ==TrackLength-1 and SUB_SEQ==int(row[2]):
                      seq_x0.append(float(row[Var]))
                      SUB_SEQ+=1
      csv_train_file.seek(0)
      x.append(seq_x)
      xO.append(seq_x0)
      SEQ+=1
  return array(x), array(xO)

StSample=1
Batch=0
FinSample=StSample+tr_samples
FinValSample=val_samples
Err_Chart_Name='/eos/experiment/ship/user/ffedship/CHARM/Evolution/Fitness_'+str(TrackLength)+'.csv'
TrSamples=FinSample-StSample
ValSamples=val_samples
print(FinValSample,ValSamples)
print('Current Track Length: ', TrackLength)
print('Learning from: ', TrSamples,' training samples...')
Xin,Xout=GiveData(StSample,FinSample,TrackLength,'x',TrainFile)
Yin,Yout=GiveData(StSample,FinSample,TrackLength,'y',TrainFile)
TXin,TXout=GiveData(StSample,FinSample,TrackLength,'tx',TrainFile)
TYin,TYout=GiveData(StSample,FinSample,TrackLength,'ty',TrainFile)
Input = np.column_stack((Xin, Yin, TXin, TYin))
Output = np.column_stack((Xout, Yout, TXout, TYout))
Output = np.array(Output)
Input = array(Input).reshape(TrSamples, TrackLength-1, features)
# define model
model = Sequential()
model.add(Masking(mask_value=666666666,input_shape=(TrackLength-1, features)))

model.add(LSTM(Nodes, activation=args.ActFunct,return_sequences='True', input_shape=(TrackLength-1, features)))
#Add dropout after each layer
model.add(Dropout(0.2))
#Extra hidden layer for a deeper learning
model.add(LSTM(Nodes, activation=args.ActFunct,return_sequences='True', input_shape=(TrackLength-1, features)))
#Add dropout after each layer
model.add(Dropout(0.2))
model.add(LSTM(Nodes, activation='Linear'))
#Output layer activation is set to Linear (Rule of thumb)
model.add(Dropout(0.2))
model.add(Dense(features))
model.compile(loss=args.LossFunct, optimizer='adam', metrics=['accuracy'])
default_weights = model.get_weights()
model.fit(Input, Output, epochs=epoc, verbose=0)
XVALin,XVALout=GiveData(1,FinValSample+1,TrackLength,'x',ValFile)
YVALin,YVALout=GiveData(1,FinValSample+1,TrackLength,'y',ValFile)
TXVALin,TXVALout=GiveData(1,FinValSample+1,TrackLength,'tx',ValFile)
TYVALin,TYVALout=GiveData(1,FinValSample+1,TrackLength,'ty',ValFile)
ValInput = np.column_stack((XVALin, YVALin, TXVALin, TYVALin))
ValInput = array(ValInput).reshape(ValSamples, TrackLength-1, features)
ValOutput = np.column_stack((XVALout, YVALout,TXVALout, TYVALout))
ValOutput = np.array(ValOutput)
OutputControl=model.predict(ValInput, verbose=0)
model_name='/eos/experiment/ship/user/ffedship/CHARM/models/model_'+str(TrackLength)
model.save(model_name)
differencex=[]
differencey=[]
differencetx=[]
differencety=[]
record=[]
for i in range(len(XVALout)):
    differencex.append(math.sqrt((ValOutput[i][0]-OutputControl[i][0]) ** 2))
    differencey.append(math.sqrt((ValOutput[i][1]-OutputControl[i][1]) ** 2))
    differencetx.append(math.sqrt((ValOutput[i][2]-OutputControl[i][2]) ** 2))
    differencety.append(math.sqrt((ValOutput[i][3]-OutputControl[i][3]) ** 2))
record.append(TrackLength)
record.append(statistics.mean(differencex))
record.append(statistics.mean(differencey))
record.append(statistics.mean(differencetx))
record.append(statistics.mean(differencety))
record.append(TrSamples)
record.append(Batch)
csv_writer_err=open(Err_Chart_Name,"w")
err_writer = csv.writer(csv_writer_err)
err_writer.writerow(record)
csv_writer_err.close()
print('Current Training batch',Batch, 'has finished')
