###############################################################################################
# import libraries
import numpy as np
import argparse
from numpy import array
import math
import ast
import csv
import copy
import statistics
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
print(bcolors.OKGREEN+'Config and Data config files have loaded succesfully...'+bcolors.ENDC)
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
################################################################################################
#Some help utility functions
def CheckForData(String):
    if String[:4]!='TEST' and String[:2]!='ID':
        return True
    return False
def RecordExistCheck(Record, Data):
    for d in Data:
        if Record==d:
            return True
    return False
def TransformVar(var, mode, shift):
    if mode == 'to':
        return (2 * (var - shift + 2000) / 4000) - 1
    if mode == 'back':
        return (((var + 1) * 4000 / 2) - 2000) + shift
def DecorateTrack(Track,data_pos,original_data_length):
    ShiftX=float(Track[original_data_length-2])
    ShiftY=float(Track[original_data_length-1])
    for nd in range(0,len(data_pos)):
       if nd==0:  #This is the custom bit that depends on the particular data structure
           Track.append(TransformVar((float(Track[data_pos[nd]])), 'to', ShiftX))
       if nd==1:  #This is the custom bit that depends on the particular data structure
           Track.append(TransformVar((float(Track[data_pos[nd]])), 'to', ShiftY))
       if nd==2:
           Track.append(float(Track[data_pos[nd]]))
       if nd==3:
           Track.append(float(Track[data_pos[nd]]))
    return Track
def CreateGhostTrack(Track,data_pos,original_data_length):
    Track[layer_id_pos]=int(Track[layer_id_pos])-1
    NewX= float(Track[data_pos[0]]) + (dZ * float(Track[data_pos[2]]))
    NewY= float(Track[data_pos[1]]) + (dZ * float(Track[data_pos[3]]))
    Track[data_pos[0]]=NewX
    Track[data_pos[1]]=NewY
    Track[layer_id_hit]='Fake'
    return Track
def PrepareOracleInput(Track):
    Output=[]
    for tr in Track:
        single_track=[]
        for st in range(len(tr)-4,len(tr)):
          single_track.append(tr[st])
        Output.append(single_track)
    return Output
def StripTrack(Track,TrackLength):
    StrippedTracks=[]
    for Hits in range(0,len(Track)):
       if Track[Hits][layer_id_hit]!='Fake':
         StrippedTracks.append(Track[Hits][:TrackLength])
    return StrippedTracks
################################################################################################
# Loading and understanding actual data
print(CU.TimeStamp(),'Loading and understanding',input_file_location,'data....')
csv_reader=open(input_file_location,"r")
data=list(csv.reader(csv_reader))
print(CU.TimeStamp(),bcolors.OKGREEN+'Data has been successfully loaded...'+bcolors.ENDC)

required_metric='TEST_'+metric+'_TRACK'

for position in range(0,len(data[0])):
    if data[0][position]=='TEST_MC_TRACK':
        track_mc_pos=position;
    if data[0][position]==required_metric:
        track_required_pos=position;
mc_tracks=[]
for d in data:
    if d[track_mc_pos]!='TEST_MC_TRACK':
         if d[track_mc_pos] in mc_tracks==False:
             mc_tracks.append(d[track_mc_pos])
print mc_tracks
exit()
print(CU.TimeStamp(),bcolors.OKGREEN+'The data column structure is adequate...'+bcolors.ENDC)
print(CU.TimeStamp(),'Testing whether we have adequate number of models to reconstruct all data sequence lengths....')

###################################################################################################
print(CU.TimeStamp(),bcolors.OKGREEN+'The reconstruction has completed',TRANN_TRACK_ID+1,'tracks have been recognised'+bcolors.ENDC)
