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
csv_writer=open(CurrDir+'DirMap',"w")
dir_writer = csv.writer(csv_writer)
string_to_write=[]
string_to_write.append('AFS_DIR')
string_to_write.append(CurrDir)
dir_writer.writerow(string_to_write)

exit()






