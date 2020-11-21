###############################################################################################
# import libraries
import numpy as np
import argparse
from numpy import array
import tensorflow as tf
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
print(bcolors.HEADER+"######################  Initialising EDER-TRANN track reconstruction module  #######################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################            Written by Filips Fedotovs            #########################"+bcolors.ENDC)
print(bcolors.HEADER+"#########################               PhD Student at UCL                 #########################"+bcolors.ENDC)
print(bcolors.HEADER+"####################################################################################################"+bcolors.ENDC)
print(bcolors.OKGREEN+'Libraries have loaded succesfully...'+bcolors.ENDC)
################################################################################################
#Loading Directory locations
csv_reader=open('../config',"r")
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

# Silence Keras warnings
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
print(CU.TimeStamp(),bcolors.OKGREEN+'Keras warning messages have been silenced....'+bcolors.ENDC)
################################################################################################


################################################################################################
# Setting parsing argument -
parser = argparse.ArgumentParser(description='Running mode')
parser.add_argument('--SIGMA', help="Please enter number of sigmas", default='5')
parser.add_argument('--GAP', help="Please enter maximum number of allowed gaps", default='1')
parser.add_argument('--f', help="Please enter the location of the initial data file", default='')
parser.add_argument('--o', help="Please enter the location of the output data file", default='')
args = parser.parse_args()
MAX_GAPS = int(args.GAP)
SIGMA_NO = int(args.SIGMA)
input_file_location=args.f
output_file_location=args.o
if input_file_location=='':
    input_file_location=EOSsubDataDIR+'/TEST_SET/RNN_TEST_SET.csv'
if output_file_location=='':
    output_file_location=EOSsubDataDIR+'/TEST_SET/RNN_TEST_SET_REC.csv'
dZ = 1315
TRANN_TRACK_ID = 0
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
features=ast.literal_eval(data_config[0][1])
feature_no=len(features)
data_features=[]
for position in range(0,len(data[0])):
    if data[0][position]=='ID_LAYER':
        layer_id_pos=position;
    if data[0][position]=='ID_HIT':
        layer_id_hit=position;
    if CheckForData(data[0][position]):
       data_features.append(data[0][position])
list_data_positions=[]
for df in range(0,len(data_features)):
     if RecordExistCheck(data_features[df], features)==False:
            print(bcolors.FAIL+'Error! The data feature',data_features[df], 'that is required in '+bcolors.ENDC,bcolors.OKBLUE+input_file_location+bcolors.ENDC,bcolors.FAIL+' set is missing from the train configuration'+bcolors.ENDC)
            exit()
for f in range(0,len(features)):
    for pos in range(0,len(data[0])):
         if CheckForData(data[0][pos]):
            if features[f]==data[0][pos]:
              list_data_positions.append(pos)
print(CU.TimeStamp(),bcolors.OKGREEN+'The data column structure is adequate...'+bcolors.ENDC)
print(CU.TimeStamp(),'Testing whether we have adequate number of models to reconstruct all data sequence lengths....')


#How many sequences (layers) are in the data?
seq_list=[]
#temp

#min_hit_id=666666666666
#max_hit_id=0
for d in data:
    if d[layer_id_pos]!='ID_LAYER':
        if (int(d[layer_id_pos]) in seq_list)==False:
                seq_list.append(int(d[layer_id_pos]))
seq_list=sorted(seq_list)
refined_data=[]
#print(min_hit_id)
#print(max_hit_id)
#exit()
for seq in seq_list:
    layer_data=[]
    for d in data:
       if d[layer_id_pos]!='ID_LAYER':
        if int(d[layer_id_pos])==seq:
            layer_data.append(d)
    refined_data.append(layer_data)
batch_list=[]
# Loading error matrix
csv_reader=open(EOSsubModelDIR+'/TrainLog.csv',"r")
raw_train_log = list(csv.reader(csv_reader))
csv_reader.close()
#Which models that were trained are available?
for seq in range(0,len(seq_list)-1):
    batch_list.append([])
    for record in raw_train_log:
        if int(record[0])==seq_list[seq]+3:
           batch_list[seq].append(int(record[6]))
for b in range(0,len(batch_list)):
    if len(batch_list[b])==0:
        print(bcolors.FAIL+'Error! The model training data is missing for track hits at layer',str(seq_list[b])+bcolors.ENDC)
        exit()
    else:
        batch_list[b]=max(batch_list[b])
#Once we worked out the completeness of trained data we load the errors from the model training that we use to set bounds on predictions
error_matrix = []
for seq in range(0,len(seq_list)-1):
    error_matrix.append([])
    for record in raw_train_log:
        if int(record[0])==seq_list[seq]+3:
            if int(record[6])==batch_list[seq]:
               error_matrix[seq].append(int(record[0]))
               for r in range(8,8+feature_no):
                   error_matrix[seq].append(float(record[r]))
print(CU.TimeStamp(),bcolors.OKGREEN+'The error matrix has loaded successfuly...'+bcolors.ENDC)
################################################################################
# Load required Keras models
model = []
for seq in range(0,len(seq_list)-1):
    print(CU.TimeStamp(),'Model loading progress: ', round(((seq+1) / len(seq_list)) * 100), ' %')
    model_name = EOSsubModelDIR+'/model_'+str(seq+3)
    model.append(tf.keras.models.load_model(model_name))
print(CU.TimeStamp(),bcolors.OKGREEN+'All models have loaded successfuly...'+bcolors.ENDC)

###################################################################################################################
def AskOracle(Input):
    Input = array(Input).reshape(1, len(Input), feature_no)
    Output = []
    Error = []
    Result = model[len(Input[0])-2].predict(Input, verbose=0)
    Output.append(list(Result[0]))
    for e in error_matrix:
        if e[0] == len(Input[0])+1:
            for r in range(1,len(e)):
              Error.append(e[r])
    Output.append(Error)
    return Output
print(CU.TimeStamp(),bcolors.OKGREEN+'The Oracle has been initialised...'+bcolors.ENDC)
##################################################################################################################
def ReconstructTrack(Hit_sequence, Layer):
    Encountered_Gaps=0
    if Encountered_Gaps<=MAX_GAPS:
     for NextLayer in range(Layer+1, max(seq_list)+1):
        if NextLayer in seq_list:
           OracleAnswer=AskOracle(PrepareOracleInput(Hit_sequence))
           ShiftX=float(Hit_sequence[0][len(Hit_sequence[0])-6])
           ShiftY=float(Hit_sequence[0][len(Hit_sequence[0])-5])
           New_Hits=[]
           for hits in range(0, len(refined_data[NextLayer])):
                DataX=float(refined_data[NextLayer][hits][list_data_positions[0]])
                DataY=float(refined_data[NextLayer][hits][list_data_positions[1]])
                DataTX=float(refined_data[NextLayer][hits][list_data_positions[2]])
                DataTY=float(refined_data[NextLayer][hits][list_data_positions[3]])
                if DataX>=(TransformVar(OracleAnswer[0][0] - (OracleAnswer[1][0] * SIGMA_NO), 'back', ShiftX)):
                  if DataX<=(TransformVar(OracleAnswer[0][0] + (OracleAnswer[1][0] * SIGMA_NO), 'back', ShiftX)):
                      if DataY>=(TransformVar(OracleAnswer[0][1] - (OracleAnswer[1][1] * SIGMA_NO), 'back', ShiftY)):
                          if DataY<=(TransformVar(OracleAnswer[0][1] + (OracleAnswer[1][1] * SIGMA_NO), 'back', ShiftY)):
                             if DataTX>=(OracleAnswer[0][2] - (OracleAnswer[1][2] * SIGMA_NO)):
                                 if DataTX<=(OracleAnswer[0][2] + (OracleAnswer[1][2] * SIGMA_NO)):
                                     if DataTY>=(OracleAnswer[0][3] - (OracleAnswer[1][3] * SIGMA_NO)):
                                        if DataTY<=(OracleAnswer[0][3] + (OracleAnswer[1][3] * SIGMA_NO)):
                                            New_Hit=copy.deepcopy(refined_data[NextLayer][hits])
                                            DX=TransformVar(DataX,'to',ShiftX)-OracleAnswer[0][0]
                                            DY=TransformVar(DataY,'to',ShiftY)-OracleAnswer[0][1]
                                            DTX=DataTX-OracleAnswer[0][2]
                                            DTY=DataTX-OracleAnswer[0][3]
                                            Difference=math.sqrt((DX**2)+(DY**2)+(DTX**2)+(DTY**2))
                                            New_Hit.append(Difference)
                                            New_Hits.append(New_Hit)
           if len(New_Hits)>0:
            New_Hits=(sorted(New_Hits,key=lambda x: float(x[len(x)-1]))[:1])[0]
            New_Hits=New_Hits[:len(New_Hits)-1]
            refined_data[NextLayer].remove(New_Hits)
            New_Hits.append(Hit_sequence[0][len(Hit_sequence[0])-7])
            New_Hits.append(ShiftX)
            New_Hits.append(ShiftY)
            New_Hits=DecorateTrack(New_Hits,list_data_positions,len(New_Hits))
            Hit_sequence.append(New_Hits)
           if len(New_Hits)==0:
            New_Hit=copy.deepcopy(refined_data[0][0])
            New_Hit[layer_id_hit]='Fake'
            New_Hit[layer_id_pos]=NextLayer
            New_Hit[list_data_positions[0]]=TransformVar(OracleAnswer[0][0], 'back', ShiftX)
            New_Hit[list_data_positions[1]]=TransformVar(OracleAnswer[0][1], 'back', ShiftY)
            New_Hit[list_data_positions[2]]=OracleAnswer[0][2]
            New_Hit[list_data_positions[3]]=OracleAnswer[0][3]
            New_Hit.append(Hit_sequence[0][len(Hit_sequence[0])-7])
            New_Hit.append(ShiftX)
            New_Hit.append(ShiftY)
            New_Hit=DecorateTrack(New_Hit,list_data_positions,len(New_Hit))
            Hit_sequence.append(New_Hit)
            Encountered_Gaps+=1
        if NextLayer in seq_list==False:
            New_Hit=copy.deepcopy(refined_data[0][0])
            New_Hit[layer_id_hit]='FAKE'
            New_Hit[layer_id_pos]=NextLayer
            New_Hit[list_data_positions[0]]=666666666
            New_Hit[list_data_positions[1]]=666666666
            New_Hit[list_data_positions[1]]=666666666
            New_Hit[list_data_positions[1]]=666666666
            New_Hit.append(Hit_sequence[0][len(Hit_sequence[0])-7])
            New_Hit.append(ShiftX)
            New_Hit.append(ShiftY)
            New_Hit=DecorateTrack(New_Hit,list_data_positions,len(New_Hit))
            Hit_sequence.append(New_Hit)
    return Hit_sequence
###################################################################################################
#Explore the layer
Hit_Counter=0
print(CU.TimeStamp(),'Starting the track reconstruction...')
for Layer in range(min(seq_list), max(seq_list)+1):
    LayerSequence=[]

    if Layer == min(seq_list):
       csv_writer_out = open(output_file_location, "w")
       out_writer = csv.writer(csv_writer_out)
       header_to_write=data[0]
       header_to_write.append('TRANN_TRACK')
       out_writer.writerow(header_to_write)
       csv_writer_out.close()
    if Layer == max(seq_list):
       for rd in refined_data[Layer]:
         TRANN_TRACK_ID+=1
         data_to_write=rd
         data_to_write.append(TRANN_TRACK_ID)
         csv_writer_out = open(output_file_location, "a")
         out_writer = csv.writer(csv_writer_out)
         out_writer.writerow(data_to_write)
         csv_writer_out.close()
    if Layer < max(seq_list):
       for rd in refined_data[Layer]:
           TRANN_TRACK_ID+=1
           hit_sequence=[]
           first_hit=copy.deepcopy(rd)
           first_hit.append(TRANN_TRACK_ID)
           ghost_hit=copy.deepcopy(first_hit)
           ghost_hit=CreateGhostTrack(ghost_hit,list_data_positions,len(ghost_hit))
           shiftX = ghost_hit[list_data_positions[0]]
           shiftY = ghost_hit[list_data_positions[1]]
           ghost_hit.append(shiftX)
           ghost_hit.append(shiftY)
           ghost_hit=DecorateTrack(ghost_hit,list_data_positions,len(ghost_hit))
           first_hit.append(shiftX)
           first_hit.append(shiftY)
           first_hit=DecorateTrack(first_hit,list_data_positions,len(first_hit))
           hit_sequence.append(ghost_hit)
           hit_sequence.append(first_hit)
           hit_sequence=ReconstructTrack(hit_sequence,Layer)
           hit_sequence=StripTrack(hit_sequence,len(rd)+1)
           LayerSequence.append(hit_sequence)

    csv_writer_out = open(output_file_location, "a")
    out_writer = csv.writer(csv_writer_out)
    for Track in LayerSequence:
        for Hit in Track:
           Hit_Counter+=1
           out_writer.writerow(Hit)
    csv_writer_out.close()
    print(CU.TimeStamp(),'Track Reconstruction progress:', int(round((float(Hit_Counter)/float(len(data)-1)*100),1)),'%')
print(CU.TimeStamp(),bcolors.OKGREEN+'The reconstruction has completed',TRANN_TRACK_ID+1,'tracks have been recognised'+bcolors.ENDC)
