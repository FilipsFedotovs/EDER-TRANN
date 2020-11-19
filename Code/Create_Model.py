ik90o/'=['#import libraries
import ast  #We need it to convert parsing string into the list
import numpy as np #We need NumPy for some math operations
import argparse #To parse model creation and training parameters to the script
from numpy import array #We will use arrays widely in this script
import tensorflow as tf  #Those are RNN related libraries
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense, Activation
from keras.layers import Dropout
from keras.layers import Masking
import math #We need it for some routine operations
import csv
import statistics

#Create_Model.py will be mainly used by other scripts to create and train models
# and a lot information will have to be passed to it for a successful operation
#This is done via
############################# Configure par
parser = argparse.ArgumentParser(description='Model creation parameters')
parser.add_argument('--DNA',help="Please enter the model dna", default='[[4, 9, 9, 0, 2], [], [], [], [], [0],[4]]')
parser.add_argument('--ValSeqStart',help="Please enter the start sequence id of the validation samples", default='1')
parser.add_argument('--ValSeqEnd',help="Please enter the final sequence id of the validation samples", default='20')
parser.add_argument('--TrainSeqStart',help="Please enter the start sequence id of the train samples", default='1')
parser.add_argument('--TrainSeqEnd',help="Please enter the final sequence id of the train samples", default='20')
parser.add_argument('--TrackLength',help="Please enter the track number", default='3')
parser.add_argument('--f',help="Please enter the user eos directory", default='.')
parser.add_argument('--Mode',help="What mode of execution would you like to: 'Test' - just to display the model fitness, 'Evolution' - to save fitness as csv, 'Production' - to save model itself, 'Train' - keep training the existing model",default='Test')
args = parser.parse_args()
#load main configuration
EOS_DIR=args.f
#Load data configuration
EOSsubDIR=EOS_DIR+'/'+'EDER-TRANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
csv_reader=open(EOSsubDataDIR+'/data_config',"r")
data_config = list(csv.reader(csv_reader))
for dc in data_config:
    if dc[0]=='FEATURES':
        features=ast.literal_eval(dc[1])

no_features=len(features)  #How many variables will we use for the RNN model?
start_val_seq=int(args.ValSeqStart) #Parsing inputs
end_val_seq=int(args.ValSeqEnd)
start_train_seq=int(args.TrainSeqStart)
end_train_seq=int(args.TrainSeqEnd)
SeqLength=int(args.TrackLength)
Mode=args.Mode
#Using Data configuration we workout what files we will use for a required job
TrainFileList=[]
TempTrainSeqList=[]
for r in range(start_train_seq,end_train_seq+1):
      TempTrainSeqList.append(r)
for tr in TempTrainSeqList:
    for dc in data_config:
      if dc[0]=='TRAIN_META' and int(dc[1])==SeqLength:
              if tr>=int(dc[2]) and tr<=int(dc[3]):
                  if (dc[4] in TrainFileList)==False:
                        TrainFileList.append(dc[4])
max_tr_seq=0
for dc in data_config:
      if dc[0]=='TRAIN_META' and int(dc[1])==SeqLength:
              if max_tr_seq<=int(dc[3]):
                   max_tr_seq=int(dc[3])
max_val_seq=0
for dc in data_config:
      if dc[0]=='VAL_META' and int(dc[1])==SeqLength:
              if max_val_seq<=int(dc[3]):
                   max_val_seq=int(dc[3])
if end_train_seq>max_tr_seq:
    end_train_seq=max_tr_seq
    print('Warning, the user requested more training samples than it is available, normalising the end training sequence to max of', end_train_seq)
if start_train_seq==0:
    start_train_seq=1
    print('Warning, the user requested invalid starting sequence, setting it to', start_train_seq)
if start_train_seq>max_tr_seq:
    start_train_seq=max_tr_seq
    print('Warning, the user requested invalid starting sequence, setting it to', start_train_seq)
if end_val_seq>max_val_seq:
    end_val_seq=max_val_seq
    print('Warning, the user requested more validation samples than it is available, normalising the end training sequence to max of', end_val_seq)
if start_val_seq==0:
    start_val_seq=1
    print('Warning, the user requested invalid starting sequence, setting it to', start_val_seq)
if start_val_seq>max_val_seq:
    start_val_seq=max_val_seq
    print('Warning, the user requested invalid starting sequence, setting it to', start_val_seq)
ValFileList=[]
TempValSeqList=[]
for r in range(start_val_seq,end_val_seq+1):
      TempValSeqList.append(r)
for tr in TempValSeqList:
    for dc in data_config:
      if dc[0]=='VAL_META' and int(dc[1])==SeqLength:
              if tr>=int(dc[2]) and tr<=int(dc[3]):
                  if (dc[4] in ValFileList)==False:
                        ValFileList.append(dc[4])
DNA=ast.literal_eval(args.DNA)
ReducedDNA=[]
for gene in DNA:
    if len(gene)==5:
        ReducedDNA.append(gene)
_=0
##############This function gives training data to LSTM model for training################################
def GiveData(StSample, FinSample, TrackLength, Variable,file):
  x=list()
  xO=list()
  required_var_pos=0
  required_seq_len_pos=0
  required_subseq_pos=0
  required_seq_pos=0
  row_iterator=0
  for f in file:
   with open(f) as csv_train_file:
    csv_reader_train = csv.reader(csv_train_file, delimiter=',')
    for SEQ in range(StSample,FinSample+1):
      seq_x=[]
      seq_x0=[]
      for SUB_SEQ in range(0,TrackLength):
        for row in csv_reader_train:
          if row_iterator==0:
             for r in range(0,len(row)):
                 if row[r]==Variable:
                      required_var_pos=r
                 if row[r]=='ID_SEQ_LENGTH':
                      required_seq_len_pos=r
                 if row[r]=='ID_SUB_SEQ':
                       required_subseq_pos=r
                 if row[r]=='ID_SEQ':
                       required_seq_pos=r
          row_iterator+=1
          if row[required_var_pos]!=Variable:
              if SEQ==int(row[required_seq_pos]):
               if TrackLength==int(row[required_seq_len_pos]):
                   if SUB_SEQ==int(row[required_subseq_pos]) and SUB_SEQ<TrackLength-1:
                      seq_x.append(float(row[required_var_pos]))
                      SUB_SEQ+=1
                   if SUB_SEQ==TrackLength-1 and SUB_SEQ==int(row[required_subseq_pos]):
                      seq_x0.append(float(row[required_var_pos]))
                      SUB_SEQ+=1
      csv_train_file.seek(0)
      x.append(seq_x)
      xO.append(seq_x0)
      SEQ+=1
  return array(x), array(xO)

act_fun_list=['linear','exponential','elu','relu', 'selu','sigmoid','softmax','softplus','softsign','tanh']
def GiveBias(Code):
    if Code==0:
        return 'False'
    if Code==1:
        return 'True'

TrSamples=(end_train_seq-start_train_seq)+1
ValSamples=(end_val_seq-start_val_seq)+1

VAin=[]
VAout=[]
for f in features:
    Vin,Vout=GiveData(start_train_seq,end_train_seq,SeqLength,f,TrainFileList)
    VAin.append(Vin)
    VAout.append(Vout)

################### Re-Arrange lists correctly ###################################
NewNewVAin=[]
for f in range(0,TrSamples):
 NewVAin=[]
 for s in range(0,SeqLength-1):
  temp=[]
  for i in VAin:
     temp.append(i[f][s])
  NewVAin.append(temp)
 NewNewVAin.append(NewVAin)
Input = array(NewNewVAin).reshape(TrSamples, SeqLength-1, no_features)
Output = np.column_stack((VAout))
###################################################################################
print('Current Track Length: ', SeqLength)
print('Attempting to learn from: ', TrSamples,' training samples...')
# define model
if Mode!='Train':
 model = Sequential()
 model.add(Masking(mask_value=666666666,input_shape=(SeqLength-1, no_features)))
 for al_no in range(len(ReducedDNA)):
   if al_no==len(ReducedDNA)-1:
      model.add(LSTM(ReducedDNA[al_no][0]*20,activation=act_fun_list[ReducedDNA[al_no][1]],recurrent_activation=act_fun_list[ReducedDNA[al_no][2]],use_bias=GiveBias(ReducedDNA[al_no][3]), input_shape=(SeqLength-1, no_features)))
      model.add(Dropout(ReducedDNA[al_no][4]/10))
   else:
      model.add(LSTM(ReducedDNA[al_no][0]*20,activation=act_fun_list[ReducedDNA[al_no][1]],recurrent_activation=act_fun_list[ReducedDNA[al_no][2]],use_bias=GiveBias(ReducedDNA[al_no][3]),return_sequences='True', input_shape=(SeqLength-1, no_features)))
      model.add(Dropout(ReducedDNA[al_no][4]/10))
 model.add(Dense(no_features))
 model.add(Activation(act_fun_list[int(DNA[5][0])]))
 model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
if Mode=='Train':
   model_name=EOSsubModelDIR+'/'+'model_'+str(SeqLength)
   model=tf.keras.models.load_model(model_name)
model.fit(Input, Output, epochs=int(DNA[6][0]*20), verbose=0)

######################################### Validation process ##############################################
ValVAin=[]
ValVAout=[]
for f in features:
    ValVin,ValVout=GiveData(start_val_seq,end_val_seq,SeqLength,f,ValFileList)
    ValVAin.append(ValVin)
    ValVAout.append(ValVout)

NewNewVAin=[]
for f in range(0,ValSamples):
 NewVAin=[]
 for s in range(0,SeqLength-1):
  temp=[]
  for i in ValVAin:
     temp.append(i[f][s])
  NewVAin.append(temp)
 NewNewVAin.append(NewVAin)
ValInput = array(NewNewVAin).reshape(ValSamples, SeqLength-1, no_features)
ValOutput = np.column_stack((ValVAout))
OutputControl=model.predict(ValInput, verbose=0)
if Mode=='Production' or Mode=='Train':
   model_name=EOSsubModelDIR+'/'+'model_'+str(SeqLength)
   model.save(model_name)
   record=[]
   record.append(SeqLength)
   for v in range(0,len(features)):
      difference_var=[]
      for i in range(ValSamples):
        difference_var.append(math.sqrt((ValOutput[i][v]-OutputControl[i][v]) ** 2))
      record.append(statistics.mean(difference_var))
   record.append(end_train_seq)
   csv_writer_err=open(EOSsubModelDIR+'/'+'model_error_'+str(SeqLength)+'.csv',"w")
   err_writer = csv.writer(csv_writer_err)
   err_writer.writerow(record)
   csv_writer_err.close()
   print('The model has been saved here:', model_name)
if Mode=='Test':
   difference=1.0
   print('Track lengths is:',SeqLength)
   print('Number of trained samples is:',TrSamples)
   difference_var=[]
   for v in range(0,len(features)):

      for i in range(len(ValOutput)):
        difference_var.append(math.sqrt((ValOutput[i][v]-OutputControl[i][v]) ** 2))
      print('The error in',features[v], 'is',statistics.mean(difference_var))
      difference*=(statistics.mean(difference_var)*3*2)

   for v in range(0,len(features)):
      count1=0
      count2=0
      count3=0
      count5=0
      for i in range(ValSamples):
        if (ValOutput[i][v]-OutputControl[i][v])<=difference_var[v]:
             count1+=1
        else:
            if (ValOutput[i][v]-OutputControl[i][v])<=difference_var[v]*2:
             count2+=1
            else:
                if (ValOutput[i][v]-OutputControl[i][v])<=difference_var[v]*3:
                    count3+=1
                else:
                   if (ValOutput[i][v]-OutputControl[i][v])<=difference_var[v]*5:
                      count5+=1
      print('-------------------------- Variable',features[v],'------------------------------------------------')
      print('% of samples within 1 mse',round(((count1/ValSamples)*100),1))
      print('% of samples within 2 mse',round((((count1+count2)/ValSamples)*100),1))
      print('% of samples within 3 mse',round((((count1+count2+count3)/ValSamples)*100),1))
      print('% of samples within 5 mse',round((((count1+count2+count3+count5)/ValSamples)*100),1))
      print('--------------------------------------------------------------------------------------------------')

   if difference!=difference:
       difference=3000
   print('The model fitness is', difference)
if Mode=='Evolution':
   record=[]
   difference=1.0
   for v in range(0,len(features)):
      difference_var=[]
      for i in range(ValSamples):
        difference_var.append(math.sqrt((ValOutput[i][v]-OutputControl[i][v]) ** 2))
      difference*=(statistics.mean(difference_var)*3*2)
   csv_writer_err=open(EOSsubEvoModelDIR+'/'+'model_fitness_'+str(SeqLength)+'_'+args.DNA+'.csv',"w")
   err_writer = csv.writer(csv_writer_err)
   record.append(SeqLength)
   if difference!=difference:
       difference=3000
   record.append(difference)
   err_writer.writerow(record)
   csv_writer_err.close()
   print('The model fitness file has been saved as ',EOSsubEvoModelDIR+'/'+'model_fitness_'+str(SeqLength)+'_'+args.DNA+'.csv')
