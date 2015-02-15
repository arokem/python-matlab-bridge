
import os

os.system('sudo apt-get install libzmq3-dev liboctave-dev')
os.system('cd ../src; mkoctfile --mex -lzmq messenger.c')
os.system('mv ../src/messenger.mex .')
os.system('cp messenger.mex ../pymatbridge/matlab')
