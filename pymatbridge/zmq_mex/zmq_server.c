#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>
#include "mex.h"
#include "zmq.h"

/* Set a 1MB receiver buffer size */
#define BUFLEN 1000000

void *ctx, *socket;
static int initialized = 0;

/* Initialize a ZMQ server */
int initialize() {
    
    ctx = zmq_ctx_new();
    socket = zmq_socket(ctx, ZMQ_REP);
    int rc = zmq_bind(socket, "ipc:///tmp/zmqmatlab");
    assert (rc == 0);
    initialized = 1;

    return 0;
}

/* Waiting for a message */
void listen(char *buffer, int buflen) {
    assert(initialized == 1);
    zmq_recv(socket, buffer, buflen, 0); 

    return;
}

/* Sending out a message */
int respond(char *msg_out, int len) {
    assert(initialzied == 1);
    int bytesent = zmq_send(socket, msg_out, len, 0);

    return bytesent;
}

/* Gateway function with Matlab */
void mexFunction(int nlhs, mxArray *plhs[], 
                 int nrhs, const mxArray *prhs[]) {

    /* Check the number of input/output arguments */
    if (nlhs != 1) {
        mexErrMsgTxt("Only 1 output argument allowed");
    } 
    if (nrhs > 2) {
        mexErrMsgTxt("Only <= 2 input argument allowed");
    }

    /* Get the input command */
    char *command;
    command = mxArrayToString(prhs[0]);

    /* Initialize a new server session */
    if (strcmp(command, "initialize") == 0) {
        assert(initialize == 0);
        
        if (!initialize()) {
            plhs[0] = mxCreateString("Initialization successful"); 
        } else {
            plhs[0] = mxCreateString("Initialization failed");
        }

        return;
 
    /* Listen over an existing socket */    
    } else if (strcmp(command, "listen") == 0) {
        char *recv_buffer;

        recv_buffer = mxCalloc(BUFLEN, sizeof(char));
        listen(recv_buffer, BUFLEN);
        plhs[0] = mxCreateString(recv_buffer);    

        return;
    } else if (strcmp(command, "respond") == 0) {
        size_t n_el = mxGetNumberOfElements(prhs[1]);
        size_t el_sz = mxGetElementSize(prhs[1]);                
        size_t msglen = n_el*el_sz;
        char *msg_out = (char*)mxGetData(prhs[1]);
       
        if (msglen == respond(msg_out, msglen)) {
            plhs[0] = mxCreateString("Data sent successfully");
        } else {
            plhs[0] = mxCreateString("Data sent unsuccessfully");
        }

        return;
    }
}
