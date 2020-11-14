#This simple script prepares test data

########################################    Import libraries    #############################################
import csv
import argparse
parser = argparse.ArgumentParser(description='select cut parameters')
parser.add_argument('--f',help="Please enter the full path to the file that you want to use as preparation dna", default='/eos/user/a/aiuliano/public/sims_fedra/CH1_pot_03_02_20/b000001/b000001_withtracks.csv')
parser.add_argument('--o',help="Please enter the full path of the destination file", default='/eos/experiment/ship/data/EDER-TRANN/TEST_SET/TEST_SET.csv')
parser.add_argument('--xmin',help="Please enter the min value of x", default='50000')
parser.add_argument('--xmax',help="Please enter the max value of x", default='60000')
parser.add_argument('--ymin',help="Please enter the min value of y", default='50000')
parser.add_argument('--ymax',help="Please enter the max value of y", default='60000')
parser.add_argument('--LossFunct',help="Please enter the loss function", default='mse')
########################################     Main body functions    #########################################
args = parser.parse_args()
flocation=args.f
olocation=args.o
xmin=args.xmin
xmax=args.xmax
ymin=args.ymin
ymax=args.ymax
with open(flocation) as csv_read_file:
          csv_read = csv.reader(csv_read_file, delimiter=',')
          data=[]
          HEADER=[]
          HEADER.append('ID_HIT')
          HEADER.append('ID_LAYER')
          HEADER.append('X')
          HEADER.append('Y')
          HEADER.append('TX')
          HEADER.append('TY')
          HEADER.append('TEST_MC_TRACK')
          HEADER.append('TEST_FEDRA_TRACK')
          data.append(HEADER)
          for row in csv_read:
           datarow=[]
           if int(row[0])!='ID':
              if float(row[2])>xmin and float(row[2])<xmax:
                  if float(row[3])>xmin and float(row[3])<xmax:
                      datarow.append(row[0])
                      datarow.append(row[1])
                      datarow.append(row[2])
                      datarow.append(row[3])
                      datarow.append(row[5])
                      datarow.append(row[6])
                      datarow.append(row[7]+'-'+row[8])
                      datarow.append(row[19])
                      data.append(datarow)
                      datarow=[]
          csv_read_file.close()
          csv_write=open(olocation,"w")
          writer = csv.writer(csv_write)
          for d in data:
           writer.writerow(d)
          csv_write.close()





