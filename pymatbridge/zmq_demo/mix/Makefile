
all:
	gcc -Wall server_c.c -o server -L/usr/local/lib -lzmq
	gcc -Wall client_c.c -o client -L/usr/local/lib -lzmq

clean:
	rm server client