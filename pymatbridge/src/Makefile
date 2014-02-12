MEXEXT = $(shell mexext)
INCLUDE = $(shell dirname $(shell find /usr -name zmq.h 2>/dev/null | head -1))
LIB = $(shell dirname $(shell find /usr -name libzmq.dylib -o -name libzmq.so 2>/dev/null | head -1))
MEX = mex -O -I$(INCLUDE) -L$(LIB) -lzmq

SRC = messenger.c
TARGET = messenger

all:
	$(MEX) $(SRC)
	mv *.$(MEXEXT) ../matlab
clean:
	rm -f ../matlab/*.$(MEXEXT)
