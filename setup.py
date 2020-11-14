#Belogs to: EDER-TRAN
#Purpose: To setup all working directories for the new user

########################################    Import libraries    #############################################
import csv
import os, shutil
import argparse
from shutil import copyfile
import subprocess

######################################## Work out whether user wants to uninstall the config ################
parser = argparse.ArgumentParser(description='Setup creation parameters')
parser.add_argument('--REMOVE',help="If you want to uninstall please enter Y", default='N')
args = parser.parse_args()
UserChoice=args.REMOVE
######################################## Create some functions to simplify the code   #######################
def FolderCreate(DIR):
    try:
      os.mkdir(DIR)
      print DIR, 'folder has been created...'
    except:
      print 'Problem creating ',DIR, 'folder, probably it already exists...'

if UserChoice=='Y':

   csv_reader=open('config',"r")
   dir_reader = csv.reader(csv_reader)
   for row in dir_reader:
     if row[0]=='EOS_DIR':
       DEL_DIR=row[1]
       DEL_DIR+='/'+'EDER-TRANN'
       shutil.rmtree(DEL_DIR)
       break
   shutil.rmtree('HTCondor')
   shutil.rmtree('Code')
   os.remove('config')

   print 'Uninstallation complete, you can delete setup.py and its parent directory manually if you wish'
   exit()

def CheckForData(String):
    if String[:4]!='TEST' and String[:2]!='ID':
        return True
    return False


def RecordExistCheck(Record, Data):
    for d in Data:
        if Record==d:
            return True
    return False
########################################     Work out and registering the current directory    #########################################
CurrDir=os.getcwd()
print 'Current directory is set as:', os.getcwd()
#Writing this directory into csv file so the software knows where to look data/code
csv_writer=open('config',"w")
dir_writer = csv.writer(csv_writer)
string_to_write=[]
string_to_write.append('AFS_DIR')
string_to_write.append(CurrDir)
dir_writer.writerow(string_to_write)
print 'Created the configuration file'

########################################     Create directories for HTCondor    #########################################
FolderCreate('HTCondor')
FolderCreate('HTCondor/MSG')
FolderCreate('HTCondor/SUB')
FolderCreate('HTCondor/SH')

#########################################   Workout EOS directory #################################
EOSDir=str(input("Please enter the full path of your directory on EOS:\n"))
#Writing this directory into csv file so the software knows where to look data/code
csv_writer=open('config',"a")
dir_writer = csv.writer(csv_writer)
string_to_write=[]
string_to_write.append('EOS_DIR')
string_to_write.append(EOSDir)
dir_writer.writerow(string_to_write)
print 'Updated the directory mapping file with EOS location'

########################################     Create sub-directories on EOS    #########################################

EOSsubDIR=EOSDir+'/'+'EDER-TRANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubTrainDIR=EOSsubDataDIR+'/'+'TRAIN_SET'
EOSsubValDIR=EOSsubDataDIR+'/'+'VALIDATION_SET'
EOSsubTestDIR=EOSsubDataDIR+'/'+'TEST_SET'

FolderCreate(EOSsubDIR)
FolderCreate(EOSsubDataDIR)
FolderCreate(EOSsubModelDIR)
FolderCreate(EOSsubEvoDIR)
FolderCreate(EOSsubTrainDIR)
FolderCreate(EOSsubValDIR)
FolderCreate(EOSsubTestDIR)

#########################################   Workout out training and validation files #################################
print 'We have to make sure that we have training and validation files in relevant folders'
print 'If you want to use original files that were created beforehand, please type "Y" below'
UserAnswer1=str(input("Would you like to copy default training and validation files? (Please put your answer in '' :\n"))
#Making action depending on user input
if UserAnswer1=='Y':
  TrainOrigin='/eos/experiment/ship/data/EDER-TRANN/TRAIN_SET/'
  src_files = os.listdir(TrainOrigin)
  for file_name in src_files:
    full_file_name = os.path.join(TrainOrigin, file_name)

    if os.path.isfile(full_file_name):
        print 'Copying file', full_file_name, 'from ',TrainOrigin,'into', EOSsubTrainDIR
        shutil.copy(full_file_name, EOSsubTrainDIR)

  ValOrigin='/eos/experiment/ship/data/EDER-TRANN/VALIDATION_SET/'
  src_files = os.listdir(ValOrigin)
  for file_name in src_files:
    full_file_name = os.path.join(ValOrigin, file_name)
    if os.path.isfile(full_file_name):
        print 'Copying file', full_file_name, 'from ',ValOrigin,'into', EOSsubValDIR
        shutil.copy(full_file_name, EOSsubValDIR)

  TestOrigin='/eos/experiment/ship/data/EDER-TRANN/TEST_SET/'
  src_files = os.listdir(TestOrigin)
  for file_name in src_files:
    full_file_name = os.path.join(TestOrigin, file_name)
    if os.path.isfile(full_file_name):
        print 'Copying file', full_file_name, 'from ',TestOrigin,'into', EOSsubTestDIR
        shutil.copy(full_file_name, EOSsubTestDIR)

#########################################   Doing initial data diagnostics #################################
print 'Performing initial data diagnostics'
Features=[]
with open(EOSsubTestDIR+'/'+'RNN_TEST_SET.csv', newline='') as f:
  reader = csv.reader(f)
  row1 = next(reader)
  print(row1)

exit()
#csv_writer=open('config',"a")
#dir_writer = csv.writer(csv_writer)
#string_to_write=[]
#string_to_write.append('EOS_DIR')
#string_to_write.append(EOSDir)
#dir_writer.writerow(string_to_write)
#print 'Updated the directory mapping file with EOS location'


exit()






