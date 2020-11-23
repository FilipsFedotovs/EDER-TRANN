#import libraries
import numpy as np
from numpy.random import randint
import argparse
import ast
import csv
import os
import random as rnd
from random import random
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Set the parsing module
parser = argparse.ArgumentParser(description='Enter training job parameters')
parser.add_argument('--MODE',help="Please enter the running mode: 'R' for reset, 'C' for continuing the training", default='C')
parser.add_argument('--TrainSamples',help="Please enter the number of training samples", default='900')
parser.add_argument('--ValSamples',help="Please enter the number of validation samples", default='1000')
args = parser.parse_args()

#setting main learning parameters
TrSamples=int(args.TrainSamples)
ValSamples=int(args.ValSamples)
mode=args.MODE
_=0

#Loading Directory locations
csv_reader=open('../config',"r")
config = list(csv.reader(csv_reader))
for c in config:
    if c[0]=='AFS_DIR':
        AFS_DIR=c[1]
    if c[0]=='EOS_DIR':
        EOS_DIR=c[1]
csv_reader.close()

#Loading Data configurations
EOSsubDIR=EOS_DIR+'/'+'EDER-TRANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
csv_reader=open(EOSsubDataDIR+'/data_config',"r")
data_config = list(csv.reader(csv_reader))
csv_reader.close()
#Working out which sequences are we training
SeqList=[]
for dc in data_config:
    if dc[0]=='VAL_META':
        if (dc[1] in SeqList)==False:
                SeqList.append(int(dc[1]))
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import CHARM_Utilities as CU
print bcolors.HEADER+"####################################################################################################"+bcolors.ENDC
print bcolors.HEADER+"#########################  Initialising EDER-TRANN model training module   #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################            Written by Filips Fedotovs            #########################"+bcolors.ENDC
print bcolors.HEADER+"#########################               PhD Student at UCL                 #########################"+bcolors.ENDC
print bcolors.HEADER+"###################### For troubleshooting please contact filips.fedotovs@cern.ch ##################"+bcolors.ENDC
print bcolors.HEADER+"####################################################################################################"+bcolors.ENDC
print CU.TimeStamp(), bcolors.OKGREEN+"Modules Have been imported successfully..."+bcolors.ENDC

print CU.TimeStamp(),'Checking whether we have available DNA codes derived from evolution'
try:
  csv_reader=open(EOSsubEvoDIR+'/Population.csv',"r")
  evolution_models=list(csv_reader)
  csv_reader.close()
except:
  print CU.TimeStamp(),bcolors.WARNING+'No evolution models have been found '+bcolors.ENDC

#This code fragment covers the Algorithm logic on the first run
if mode=='R':
 CU.TrainCleanUp(AFS_DIR, EOS_DIR,'Full')
 print CU.TimeStamp(),bcolors.BOLD+'What model configurations would you like to use for training?'+bcolors.ENDC
 print bcolors.BOLD+'If you would like to use Evolution derived Models please press E'+bcolors.ENDC
 print bcolors.BOLD+'If you would like to use default model setting (aka Vanilla RNN) please enter D'+bcolors.ENDC
 print bcolors.BOLD+'If you would like to specify for each seq length a particular configuration, please enter C'+bcolors.ENDC
 UserAnswer=raw_input(bcolors.BOLD+"Please, enter your option\n"+bcolors.ENDC)
 if UserAnswer=='D':
         job_list=[]
         for seq in SeqList:
          job=[]
          job.append(seq)
          job.append(1)
          job.append(TrSamples)
          job.append(1)
          job.append(ValSamples)
          job.append('-')
          job_list.append(job)
         print CU.TimeStamp(),bcolors.OKGREEN+'Job list has been created'+bcolors.ENDC
 if UserAnswer=='E':
    refined_evolution_models=[]
    for seq_no in range(0,max(SeqList)+1):
        refined_evolution_models.append([])
    for seq in SeqList:
     for em in evolution_models:
      try:
       if seq==ast.literal_eval(em)[0]:
          refined_evolution_model=[]
          refined_evolution_model.append(ast.literal_eval(em)[0])
          refined_evolution_model.append(0)
          refined_evolution_model.append(TrSamples)
          refined_evolution_model.append(0)
          refined_evolution_model.append(ValSamples)
          refined_evolution_model.append(ast.literal_eval(ast.literal_eval(em)[4]))
          refined_evolution_model.append(ast.literal_eval(em)[5])
          refined_evolution_models[seq].append(refined_evolution_model)
      except:
       print bcolors.FAIL+'Error reading one of the records'+bcolors.ENDC
    for em in range(0,len(refined_evolution_models)):
        if len(refined_evolution_models[em])>0:
            refined_evolution_models[em]= (sorted(refined_evolution_models[em],key=lambda x: float(x[6]),reverse=False)[:1])
    for seq in SeqList:
      if len(refined_evolution_models[seq])>0:
           refined_evolution_models[seq]=refined_evolution_models[seq][0]
      else:
          print CU.TimeStamp(),bcolors.BOLD+'Despite using Evolution derived models the model which deals with sequences of length',seq,'is missing'+bcolors.ENDC
          print bcolors.BOLD+'Enter the DNA code for the missing sequence here or just enter D to use default model setting'+bcolors.ENDC
          UserAnswer=raw_input(bcolors.BOLD+"Please, enter your option\n"+bcolors.ENDC)
          if UserAnswer=='D':
           refined_evolution_models[seq].append(seq)
           refined_evolution_models[seq].append(0)
           refined_evolution_models[seq].append(TrSamples)
           refined_evolution_models[seq].append(0)
           refined_evolution_models[seq].append(ValSamples)
           refined_evolution_models[seq].append('-')
          else:
           refined_evolution_models[seq].append(seq)
           refined_evolution_models[seq].append(0)
           refined_evolution_models[seq].append(TrSamples)
           refined_evolution_models[seq].append(0)
           refined_evolution_models[seq].append(ValSamples)
           refined_evolution_models[seq].append(ast.literal_eval(UserAnswer))
    job_list=[]
    for records in refined_evolution_models:
        job_list.append(records[:6])
 if UserAnswer=='C':
         job_list=[]
         for seq in SeqList:
          print CU.TimeStamp(),bcolors.BOLD+'For sequence',seq,'please type model DNA'+bcolors.ENDC
          print CU.TimeStamp(),bcolors.BOLD+'The format is as follows [[x0,...,x4],[x0,...,x4],[x0,...,x4],[x0,...,x4],[x0,...,x4],[y],[z]]]'+bcolors.ENDC
          print CU.TimeStamp(),bcolors.BOLD+'Please consult documentation for accepted ranges'+bcolors.ENDC
          UserAnswer=raw_input(bcolors.BOLD+"Please, enter it here:\n"+bcolors.ENDC)
          job=[]
          job.append(seq)
          job.append(0)
          job.append(TrSamples)
          job.append(0)
          job.append(ValSamples)
          job.append(ast.literal_eval(UserAnswer))
          job_list.append(job)
         print CU.TimeStamp(),bcolors.OKGREEN+'Job list has been created'+bcolors.ENDC

         exit()
 for job in range(0,len(job_list)):
    job_list[job].append(0)
    job_list[job].append(0)
    for dc in ast.literal_eval(data_config[0][1]):
     job_list[job].append(3000)
 CU.LogOperations(EOSsubModelDIR+'/TrainLog.csv','StartLog',job_list)
 CU.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,job_list,'New')
 print bcolors.BOLD+"Please check them in few hours"+bcolors.ENDC
if mode=='C':
   Batch=0
   print CU.TimeStamp(),'Continuing the training that has been started before'
   csv_reader=open(EOSsubModelDIR+'/TrainLog.csv',"r")
   PreviousJobs = list(csv.reader(csv_reader))
   csv_reader.close()
   ###Working out the latest batch
   for j in PreviousJobs:
       if int(j[6])>Batch:
           Batch=int(j[6])
   ###Working out the remaining jobs
   RemainingJobs=[]
   for j in PreviousJobs:
       if int(j[6])==Batch:
           if int(j[7])==0:
               file_name=EOSsubModelDIR+'/model_error_'+j[0]+'.csv'
               try:
                csv_reader=open(file_name,"r")
                result = list(csv.reader(csv_reader))
                j[7]=1
                for dc in range(0,len(ast.literal_eval(data_config[0][1]))):
                    j[8+dc]=result[0][dc+1]
                os.remove(file_name)
               except:
                RemainingJobs.append(j)
   CU.LogOperations(EOSsubModelDIR+'/TrainLog.csv','StartLog',PreviousJobs)
   if len(RemainingJobs)>0:
     print CU.TimeStamp(),bcolors.WARNING+'Warning, there are still', len(RemainingJobs), 'HTCondor jobs remaining'+bcolors.ENDC
     print bcolors.BOLD+'If you would like to wait and try again later please enter W'+bcolors.ENDC
     print bcolors.BOLD+'If you would like to resubmit please enter R'+bcolors.ENDC
     UserAnswer=raw_input(bcolors.BOLD+"Please, enter your option\n"+bcolors.ENDC)
     if UserAnswer=='W':
         print CU.TimeStamp(),'OK, exiting now then'
         exit()
     if UserAnswer=='R':
        if Batch==0:
          CU.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,RemainingJobs,'New')
        if Batch>0:
          CU.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,RemainingJobs,'Train')
        print CU.TimeStamp(), bcolors.OKGREEN+"All jobs for batch ",Batch,"have been resubmitted"+bcolors.ENDC
        print bcolors.BOLD+"Please check them in few hours"+bcolors.ENDC
        exit()
   if len(RemainingJobs)==0:
      NextJobs=[]
      print CU.TimeStamp(),'Creating next batch',Batch+1
      for record in range(0,len(PreviousJobs)):
          if int(PreviousJobs[record][6])==Batch:
                 PreviousJobs[record][6]=int(PreviousJobs[record][6])+1
                 PreviousJobs[record][1]=int(PreviousJobs[record][2])+1
                 PreviousJobs[record][2]=int(PreviousJobs[record][1])+TrSamples
                 PreviousJobs[record][3]=int(PreviousJobs[record][4])+1
                 PreviousJobs[record][4]=int(PreviousJobs[record][3])+TrSamples
                 PreviousJobs[record][7]=0
                 NextJobs.append(PreviousJobs[record])

      CU.TrainCleanUp(AFS_DIR,EOS_DIR,'Partial')
      print bcolors.BOLD+'Batch',Batch,' is completed'+bcolors.ENDC
      print bcolors.BOLD+'Would you like to continue training?'+bcolors.ENDC
      UserAnswer=raw_input(bcolors.BOLD+"Please, enter Y/N\n"+bcolors.ENDC)
      if UserAnswer=='Y':
          CU.LogOperations(EOSsubModelDIR+'/TrainLog.csv','UpdateLog',NextJobs)
          CU.SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,NextJobs,'Train')
          print CU.TimeStamp(),bcolors.OKGREEN+'The next batch',Batch+1,'has been submitted to HTCondor'+bcolors.ENDC
          print bcolors.BOLD,'Please run the script in few hours with --MODE C setting'+bcolors.ENDC

      if UserAnswer=='N':
          print CU.TimeStamp(),bcolors.OKGREEN+'Training is finished then, thank you and good bye'+bcolors.ENDC
exit()


