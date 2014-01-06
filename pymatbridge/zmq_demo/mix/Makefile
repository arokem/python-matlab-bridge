CC = gcc
CFLAGS = -Wall
LIBS = -L/usr/local/lib -lzmq

all: cServer cClient

cServer: server_c.c
	$(CC) $(CFLAGS) $(LIBS) server_c.c -o cServer 

cClient: client_c.c
	$(CC) $(CFLAGS) $(LIBS) client_c.c -o cClient 

clean:
	rm -f cServer cClient
