#Belogs to: EDER-TRAN
#Purpose: To setup all working directories for the new user

########################################    Import libraries    #############################################
import csv
import os, shutil
import subprocess
########################################     Work out and registering the current directory    #########################################
CurrDir=os.getcwd()
print 'Current directory is set as:', os.getcwd()
#Writing this directory into csv file so the software knows where to look data/code
csv_writer=open('DirMap',"w")
dir_writer = csv.writer(csv_writer)
string_to_write=[]
string_to_write.append('AFS_DIR')
string_to_write.append(CurrDir)
dir_writer.writerow(string_to_write)
print 'Created the directory mapping file'

########################################     Create directories for HTCondor    #########################################
try:
  os.mkdir('HTCondor')
  print 'HTCondor folder has been created:'
except:
  print 'Problem creating HTCondor directory, probably it already exists'
try:
  os.mkdir('HTCondor/MSG')
  print 'HTCondor/MSG sub-folder has been created:'
except:
  print 'Problem creating HTCondor/MSG sub-directory, probably it already exists'
try:
  os.mkdir('HTCondor/SUB')
  print 'HTCondor/SUB sub-folder has been created:'
except:
  print 'Problem creating HTCondor/SUB sub-directory, probably it already exists'
try:
  os.mkdir('HTCondor/SH')
  print 'HTCondor/SH sub-folder has been created:'
except:
  print 'Problem creating HTCondor/SH sub-directory, probably it already exists'


#########################################   Workout EOS directory #################################
EOSDir=str(input("Please enter the full path of your directory on EOS:\n"))
print(EOSDir)

exit()






