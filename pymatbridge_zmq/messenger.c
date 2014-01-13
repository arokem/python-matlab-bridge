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
int initialize(char *socket_addr) {
    
    ctx = zmq_ctx_new();
    socket = zmq_socket(ctx, ZMQ_REP);
    int rc = zmq_bind(socket, socket_addr);
    
    if (!rc) {
        initialized = 1;
        return 0;
    } else {
        return -1;
    }
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

    /* If no input argument, print out the usage */ 
    if (nrhs == 0) {
        mexErrMsgTxt("Usage: messenger('init|listen|respond', extra1, extra2, ...)");
    }

    /* Get the input command */
    char *cmd;
    if(!(cmd = mxArrayToString(prhs[0]))) {
        mexErrMsgTxt("Cannot read the command");
    }

    /* Initialize a new server session */
    if (strcmp(cmd, "init") == 0) {
        char *socket_addr;
        mxLogical *p;
        
        /* Check if the input format is valid */
        if (nrhs != 2) {
            mexErrMsgTxt("Missing argument: socket address");
        } 
        if (!(socket_addr = mxArrayToString(prhs[1]))) {
            mexErrMsgTxt("Cannot read socket address");
        }

        plhs[0] = mxCreateLogicalMatrix(1, 1);
        p = mxGetLogicals(plhs[0]);
        
        if (!initialized) {
            if (!initialize(socket_addr)) {
                p[0] = true;
                mexPrintf("Socket created at: %s", socket_addr);
            } else {
                p[0] = false;
                mexErrMsgTxt("Socket creation failed.");
            }
        } else {
            mexErrMsgTxt("One socket has already been initialized.");
        }

        return;
 
    /* Listen over an existing socket */    
    } else if (strcmp(cmd, "listen") == 0) {
        char *recv_buffer;

        recv_buffer = mxCalloc(BUFLEN, sizeof(char));
        listen(recv_buffer, BUFLEN);
        plhs[0] = mxCreateString(recv_buffer);    

        return;
    } else if (strcmp(cmd, "respond") == 0) {
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
