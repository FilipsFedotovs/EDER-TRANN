# EDER-TRANN
Emulsion Data Event Reconstruction - Tracking using Reccurent Artificial Neural Networks

This README just serves as a very short user guide, the documentation will be written much later

------------------------------------  Installation steps:   ----------------------------------------------------------------------------------------

1) pip3 install tensorflow --user
2) go to your home directory in afs where you would like to install the package
3) git clone https://github.com/FilipsFedotovs/EDER-TRANN/
4) cd EDER-TRANN/
5) python setup.py
6) The installation will require an EOS directory, please enter the location on EOS where you would like to keep data and the models. AN example of the input is /eos/experiment/ship/user/username
7) The installation will ask whether you want to copy default training and validation files (that were prepared earlier). Unless you have your own, please enter Y.
--- The installer will copy and analyse existing data, it might take 5-10 minutes---
8) if the message 'EDER-TRANN setup is successfully completed' is displayed, it means that the package is ready for work.

------------------------------------  Model creation and training ---------------------------------------------------------------------------------
1) python Model_Training.py --MODE R --TrainSamples TRAINSAMPLES --ValSamples VALSAMPLES
---TRAINSAMPLES and VALSAMPLES are the integer numbers for number of Training and Validation samples used to train the model. Without those options the TrainSamples are set to 500 as a default and ValSamples are set to 1000. (It is discouraged to use more samples per training as it can lead to jobs to be killed by HTCondor).
2) The script will ask which samples to use. The allowed options are D (default vanilla RNN model), 





