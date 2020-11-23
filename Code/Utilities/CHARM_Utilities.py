#This file contains all utilities for csv write-read operations

########################################    Import libraries    #############################################
import csv
import os, shutil
import subprocess
import copy
import time as t
import datetime
_=0
########################################     Main body functions    #########################################
def LogOperations(flocation,mode, message):
    if mode=='UpdateLog':
        csv_writer_log=open(flocation,"a")
        log_writer = csv.writer(csv_writer_log)
        for m in message:
         log_writer.writerow(m)
        csv_writer_log.close()
    if mode=='StartLog':
        csv_writer_log=open(flocation,"w")
        log_writer = csv.writer(csv_writer_log)
        for m in message:
         log_writer.writerow(m)
        csv_writer_log.close()
def TimeStamp():
 return "["+datetime.datetime.now().strftime("%D")+' '+datetime.datetime.now().strftime("%H:%M:%S")+"]"
def EvolutionCleanUp(AFS_DIR, EOS_DIR,mode):
      subprocess.call(['condor_rm', '-all'])
      if mode=='Full':
       EOSsubDIR=EOS_DIR+'/'+'EDER-TRANN'
       EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
       EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
       folder =  EOSsubEvoDIR
       for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

       folder =  EOSsubEvoModelDIR
       for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

      folder =  AFS_DIR+'/HTCondor/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
def SubmitEvoJobsCondor(AFS_DIR,EOS_DIR,population,tr_start,tr_end, val_start, val_end):
    for p in population:
            SHName=AFS_DIR+'/HTCondor/SH/SH_'+str(p)+'.sh'
            SUBName=AFS_DIR+'/HTCondor/SUB/SUB_'+str(p)+'.sub'
            MSGName='MSG_'
            OptionLine=' --Mode Evolution'
            OptionLine+=(' --DNA "'+str(p[4])+'"')
            OptionLine+=(" --ValSeqStart "+str(val_start))
            OptionLine+=(" --ValSeqEnd "+str(val_end))
            OptionLine+=(" --TrainSeqStart "+str(tr_start))
            OptionLine+=(" --TrainSeqEnd "+str(tr_end))
            OptionLine+=(" --TrackLength "+str(p[0]))
            OptionLine+=(" --f "+EOS_DIR)
            MSGName+=str(p)
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
            f.write("output ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".out")
            f.write("\n")
            f.write("error ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".err")
            f.write("\n")
            f.write("log ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".log")
            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            TotalLine='python3 '+AFS_DIR+'/Code/Create_Model.py '+OptionLine
            f = open(SHName, "w")
            f.write("#!/bin/bash")
            f.write("\n")
            f.write("set -ux")
            f.write("\n")
            f.write(TotalLine)
            f.write("\n")
            f.close()
            subprocess.call(['condor_submit',SUBName])
            print(TotalLine," has been successfully submitted")
def SubmitTrainJobsCondor(AFS_DIR,EOS_DIR,job_list,mode):
    for job in job_list:
            SHName=AFS_DIR+'/HTCondor/SH/SH_'+str(job[0])+'_'+str(job[6])+'.sh'
            SUBName=AFS_DIR+'/HTCondor/SUB/SUB_'+str(job[0])+'_'+str(job[6])+'.sub'
            MSGName='MSG_'
            if mode=='New':
                OptionLine=' --Mode Production'
            else:
                OptionLine=' --Mode Train'
            if job[5]!='-':
               OptionLine+=(' --DNA "'+str(job[5])+'"')
            OptionLine+=(" --ValSeqStart "+str(job[3]))
            OptionLine+=(" --ValSeqEnd "+str(job[4]))
            OptionLine+=(" --TrainSeqStart "+str(job[1]))
            OptionLine+=(" --TrainSeqEnd "+str(job[2]))
            OptionLine+=(" --TrackLength "+str(job[0]))
            OptionLine+=(" --f "+EOS_DIR)
            MSGName+=(str(job[0])+'_'+str(job[6]))
            f = open(SUBName, "w")
            f.write("executable = "+SHName)
            f.write("\n")
            f.write("output ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".out")
            f.write("\n")
            f.write("error ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".err")
            f.write("\n")
            f.write("log ="+AFS_DIR+"/HTCondor/MSG/"+MSGName+".log")
            f.write("\n")
            f.write('requirements = (CERNEnvironment =!= "qa")')
            f.write("\n")
            f.write('transfer_output_files = ""')
            f.write("\n")
            f.write('+JobFlavour = "workday"')
            f.write("\n")
            f.write('queue 1')
            f.write("\n")
            f.close()
            TotalLine='python3 '+AFS_DIR+'/Code/Create_Model.py '+OptionLine
            f = open(SHName, "w")
            f.write("#!/bin/bash")
            f.write("\n")
            f.write("set -ux")
            f.write("\n")
            f.write(TotalLine)
            f.write("\n")
            f.close()
            subprocess.call(['condor_submit',SUBName])
            print(TotalLine," has been successfully submitted")
def TrainCleanUp(AFS_DIR, EOS_DIR,mode):
    if mode=='Full':
      subprocess.call(['condor_rm', '-all'])
      EOSsubDIR=EOS_DIR+'/'+'EDER-TRANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Models'
      folder =  EOSsubModelDIR
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

      folder =  AFS_DIR+'/HTCondor/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
    else:
      EOSsubDIR=EOS_DIR+'/'+'EDER-TRANN'
      EOSsubModelDIR=EOSsubDIR+'/'+'Models'
      folder =  EOSsubModelDIR
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path) and 'error' in file_path:
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SH'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/SUB'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
      folder =  AFS_DIR+'/HTCondor/MSG'
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

