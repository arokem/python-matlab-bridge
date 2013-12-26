#include <stdio.h>
#include <zmq.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>

int main (void) {
    
    void *context = zmq_ctx_new ();
    void *responder = zmq_socket (context, ZMQ_REP);
    int rc = zmq_bind(responder, "ipc:///tmp/ipctest");
    assert (rc == 0);

    while(1) {
        char buffer[1024];
        zmq_recv(responder, buffer, 1024, 0);
        printf("Got a request: %s\n", buffer);
        sleep(5);
        char *msg_out = "World";
        zmq_send(responder, msg_out, 5, 0);
        printf("Sending out message: %s\n", msg_out);
    }
    
    return 0;
}

