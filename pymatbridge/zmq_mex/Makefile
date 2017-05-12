MEX = mex -O -I/usr/local/include -L/usr/local/lib -lzmq
MEXEXT = $(shell mexext)
SRC = zmq_server.c
TARGET = zmqmex

all: $(TARGET)

$(TARGET): $(SRC)
	$(MEX) $(SRC) 

clean:
	rm -f *.$(MEXEXT)
