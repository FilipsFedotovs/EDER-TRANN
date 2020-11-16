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
parser.add_argument('--DTEST',help="If you want to do Data Test only", default='N')
args = parser.parse_args()
UserChoice=args.REMOVE
UserChoice2=args.DTEST
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
UserAnswer1=str(input("Would you like to copy default training and validation files? (Please put your answer in ''):\n"))
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
with open(EOSsubTestDIR+'/'+'RNN_TEST_SET.csv') as f:
  reader = csv.reader(f)
  row1 = next(reader)
  for r in row1:
     if CheckForData(r):
        Features.append(r)
f.close()
print 'The test data set contains', len(Features), 'features:', Features
print 'Testing whether the training sets is adequate...'
csv_writer=open(EOSsubDataDIR+'/data_config',"w")
dir_writer = csv.writer(csv_writer)
string_to_write=[]
string_to_write.append('FEATURES')
string_to_write.append(Features)
dir_writer.writerow(string_to_write)
csv_writer.close()
src_files = os.listdir(EOSsubTrainDIR)
for file_name in src_files:
    TrainFeatures=[]
    full_file_name = os.path.join(EOSsubTrainDIR, file_name)
    if os.path.isfile(full_file_name):
        print 'Training set', full_file_name, '...'
        with open(full_file_name) as f:
            reader = csv.reader(f)
            row1 = next(reader)
            for ft in Features:
             if RecordExistCheck(ft, row1)==False:
                 print('Error! The data feature',ft, 'that is required in Test Data set is missing from ',full_file_name)
                 exit()
print 'Looks like the training set is adequate...'
f.close()

print 'Testing whether the validation set is adequate...'
src_files = os.listdir(EOSsubValDIR)
for file_name in src_files:
    full_file_name = os.path.join(EOSsubValDIR, file_name)
    if os.path.isfile(full_file_name):
        print 'Validation set', full_file_name, '...'
        with open(full_file_name) as f:
            reader = csv.reader(f)
            row1 = next(reader)
            for ft in Features:
             if RecordExistCheck(ft, row1)==False:
                 print('Error! The data feature',ft, 'that is required in Test Data set is missing from ',full_file_name)
                 exit()
f.close()
print 'Looks like the validation set is adequate...'

############################## Create metadata #####################################
print 'Creating meta-data...'
src_files = os.listdir(EOSsubValDIR)
for file_name in src_files:
    full_file_name = os.path.join(EOSsubValDIR, file_name)
    if os.path.isfile(full_file_name):
        print 'Analysing validation set', full_file_name, '...'
        with open(full_file_name) as f:
         for l in range(0,100):
            ID_SEQ=[]
            ID_LEN_EXISTS=False
            reader = csv.reader(f)
            reader_lines=list(reader)
            required_idseq_row=0
            required_idseqlen_row=0
            for r in range(0,reader_lines[0]):
                if reader_lines[0][r]=='ID_SEQ':
                    required_idseq_row=r
                if reader_lines[0][r]=='ID_SEQ_LENGTH':
                    required_idseqlen_row=r
            for line in reader_lines:
                if line[required_idseqlen_row]!='ID_SEQ_LENGTH':
                    if int(line[required_idseqlen_row])==l:
                       ID_LEN_EXISTS=True
                       if line[required_idseq_row]!='ID_SEQ':
                          ID_SEQ.append(int(line[required_idseq_row]))
            if ID_LEN_EXISTS:
                csv_writer=open(EOSsubDataDIR+'/data_config',"a")
                dir_writer = csv.writer(csv_writer)
                string_to_write=[]
                string_to_write.append('VAL_META')
                string_to_write.append(l)
                string_to_write.append(min(ID_SEQ))
                string_to_write.append(max(ID_SEQ))
                string_to_write.append(full_file_name)
                dir_writer.writerow(string_to_write)
                csv_writer.close()
        f.close()

exit()









