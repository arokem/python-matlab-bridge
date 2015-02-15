

all: 
	sudo apt-get install libzmq3-dev liboctave-dev
	cd ../src; mkoctfile --mex -lzmq messenger.c
	mv ../src/messenger.mex .
	cp messenger.mex ../pymatbridge/matlab
