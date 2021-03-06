# EDER-TRANN
Emulsion Data Event Reconstruction - Tracking using Reccurent Artificial Neural Networks

This README just serves as a very short user guide, the documentation will be written much later

------- Installation steps --------

1) pip3 install tensorflow --user
2) pip3 install keras==2.3.1 --user
3) go to your home directory in afs where you would like to install the package
4) git clone https://github.com/FilipsFedotovs/EDER-TRANN/
5) cd EDER-TRANN/
6) python setup.py
7) The installation will require an EOS directory, please enter the location on EOS where you would like to keep data and the models. An example of the input is /eos/experiment/ship/user/username (but create the directory there first).
8) The installation will ask whether you want to copy default training and validation files (that were prepared earlier). Unless you have your own, please enter Y.     The installer will copy and analyse existing data, it might take 5-10 minutes
9) if the message 'EDER-TRANN setup is successfully completed' is displayed, it means that the package is ready for work

-------- Model creation and training -------
1) Go to EDER_TRANN directory on AFS
2) cd Code
3) python Model_Training.py --MODE R
4) The script will ask which samples to use. Please type D and press ENTER.The script will send HTCondor jobs and exit.
5) After a day or so please run: python Model_Training.py --MODE C
6) This process is repeated multiple times until the model is sufficinetly trained

------- Track reconstruction --------
1) Go to EDER_TRAN directory on AFS
2) cd Code 
3) tmux (please note the number of lxplus machine at which tmux session is logged in)
4) kinit username@CERN.CH -l 24h00m
5) python3 Track_Reconstructor.py 
   The process can take many hours, log out of tmux by using ctrl+b

------ Hit utilisation Analysis -------
1) Relogin to the same machine by using ssh -XY username@lxplus#.cern.ch where # is the recorded number.
2) tmux a -t 0
3) if the green message "The reconstruction has completed # tracks have been recognised' is displayed, it means that the reconstruction is finished.
4) kinit username@CERN.CH
5) cd Utilisation
6) python Analyse_Hit_Utilisation.py --metric TRANN




