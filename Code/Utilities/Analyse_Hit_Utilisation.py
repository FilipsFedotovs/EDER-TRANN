###############################################################################################
# import libraries
import numpy as np
import argparse
from numpy import array
import math
import ast
import csv
import copy
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
print(bcolors.HEADER+"####################################################################################################"+bcolors.ENDC)
print(bcolors.HEADER+"######################    Initialising EDER-TRANN hit utilisation analyser   #######################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################            Written by Filips Fedotovs            #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################               PhD Student at UCL                 #########################"+bcolors.ENDC)
print(bcolors.HEADER+"####################################################################################################"+bcolors.ENDC)
print(bcolors.OKGREEN+'Libraries have loaded succesfully...'+bcolors.ENDC)
################################################################################################
#Loading Directory locations
csv_reader=open('../../config',"r")
config = list(csv.reader(csv_reader))
for c in config:
    if c[0]=='AFS_DIR':
        AFS_DIR=c[1]
    if c[0]=='EOS_DIR':
        EOS_DIR=c[1]

#Loading Data configurations
EOSsubDIR=EOS_DIR+'/'+'EDER-TRANN'
EOSsubDataDIR=EOSsubDIR+'/'+'Data'
EOSsubModelDIR=EOSsubDIR+'/'+'Models'
EOSsubEvoDIR=EOSsubDIR+'/'+'Evolution'
EOSsubEvoModelDIR=EOSsubEvoDIR+'/'+'Models'
csv_reader=open(EOSsubDataDIR+'/data_config',"r")
data_config = list(csv.reader(csv_reader))
print bcolors.OKGREEN+'Config and Data config files have loaded succesfully...'+bcolors.ENDC
################################################################################################
import sys
sys.path.insert(1, AFS_DIR+'/Code/Utilities/')
import CHARM_Utilities as CU

################################################################################################
# Setting parsing argument -
parser = argparse.ArgumentParser(description='Running mode')
parser.add_argument('--f', help="Please enter the location of the initial data file", default='')
parser.add_argument('--metric', help="Please enter the metric to compare (FEDRA/TRANN/MC)", default='TRANN')
args = parser.parse_args()
input_file_location=args.f
if input_file_location=='':
    input_file_location=EOSsubDataDIR+'/TEST_SET/RNN_TEST_SET_REC.csv'
metric=args.metric

################################################################################################
# Loading and understanding actual data
print CU.TimeStamp(),'Loading and understanding',input_file_location,'data....'
csv_reader=open(input_file_location,"r")
data=list(csv.reader(csv_reader))
print CU.TimeStamp(),bcolors.OKGREEN+'Data has been successfully loaded...'+bcolors.ENDC

required_metric='TEST_'+metric+'_TRACK'
print CU.TimeStamp(),'Analysing Monte-Carlo track information...'
for position in range(0,len(data[0])):
    if data[0][position]=='TEST_MC_TRACK':
        track_mc_pos=position;
    if data[0][position]==required_metric:
        track_required_pos=position;
mc_tracks=[]
for d in data:
    if d[track_mc_pos]!='TEST_MC_TRACK':
        mc_track=[]
        mc_track.append(d[track_mc_pos])
        if (mc_track in mc_tracks)==False:
             mc_tracks.append(mc_track)

print CU.TimeStamp(),bcolors.OKGREEN+str(len(mc_tracks)),' Monte-Carlo tracks have been identified'+bcolors.ENDC
for mt in mc_tracks:
    mc_track_no=0
    for d in data:
        if d[track_mc_pos]==mt[0]:
            mc_track_no+=1
    mt.append(mc_track_no)

refined_mc_tracks=[]
for mt in mc_tracks:
    if mt[1]>1:
      refined_mc_tracks.append(mt)
print CU.TimeStamp(),bcolors.OKGREEN+str(len(refined_mc_tracks)),' Monte-Carlo tracks have been identified with lengths>1 hit in the sequence'+bcolors.ENDC

for mt in refined_mc_tracks:
    required_tracks=[]
    required_track=[]
    for d in data:
        if d[track_mc_pos]==mt[0]:
            required_track=[(d[track_required_pos])]
            required_track.append(0)
            if (required_track in required_tracks)==False:
                  required_tracks.append(required_track)
    mt.append(required_tracks)
for mt in refined_mc_tracks:
    required_tracks=[]
    required_track=[]
    for d in data:
        if d[track_mc_pos]==mt[0]:
           for rt in mt[2]:
               req_track_no=0
               if rt[0]==d[track_required_pos]:
                   rt[1]+=1

for mt in refined_mc_tracks:
    mt[2]=sorted(mt[2],key=lambda x: float(x[1]),reverse=True)[:1]
mc_hits=0
req_hits=0
for mt in refined_mc_tracks:
    mc_hits+=mt[1]
    req_hits+=mt[2][0][1]
utilisation=round((float(req_hits)/float(mc_hits)),1)*100

print CU.TimeStamp(),bcolors.OKGREEN+'The hit utilisation for',required_metric,'tracks is',bcolors.BOLD+str(utilisation),' %'+bcolors.ENDC

