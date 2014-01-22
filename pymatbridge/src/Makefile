MEX = mex -O -I/usr/local/include -L/usr/local/lib -lzmq
MEXEXT = $(shell mexext)
SRC = messenger.c
TARGET = messenger

all: 
	$(MEX) $(SRC) 
	mv *.$(MEXEXT) ../matlab_zmq
clean:
	rm -f *.$(MEXEXT)
