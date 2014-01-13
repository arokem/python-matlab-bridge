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

/* Listen over an existing socket 
 * Now the receiver buffer is pre-allocated
 * In the future we can possibly use multi-part messaging 
 */
int listen(char *buffer, int buflen) {
    if (!initialized) {
        mexErrMsgTxt("Error: ZMQ session not initialized");
    }
    
    return zmq_recv(socket, buffer, buflen, 0); 
}

/* Sending out a message */
int respond(char *msg_out, int len) {
    if (!initialized) {
        mexErrMsgTxt("Error: ZMQ session not initialized");
    }
    
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
                mexPrintf("Socket created at: %s\n", socket_addr);
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
        char *recv_buffer = mxCalloc(BUFLEN, sizeof(char));

        int byte_recvd = listen(recv_buffer, BUFLEN);
        
        /* Check if the received data is complete and correct */
        if ((byte_recvd > -1) && (byte_recvd <= BUFLEN)) {
            plhs[0] = mxCreateString(recv_buffer);    
        } else if (byte_recvd > BUFLEN){
            mexErrMsgTxt("Receiver buffer overflow. Message truncated");
        } else {
            mexErrMsgTxt("Failed to receive a message due to ZMQ error.");
        }
        
        return;

    /* Send a message out */
    } else if (strcmp(cmd, "respond") == 0) {
        mxLogical *p;

        /* Check if the input format is valid */
        if (nrhs != 2) {
            mexErrMsgTxt("Please provide the message to send");
        } 
        
        size_t msglen = mxGetNumberOfElements(prhs[1]) * mxGetElementSize(prhs[1]);
        char *msg_out = (char*)mxGetData(prhs[1]);
        plhs[0] = mxCreateLogicalMatrix(1, 1);
        p = mxGetLogicals(plhs[0]);

        if (msglen == respond(msg_out, msglen)) {
            p[0] = true;
            mexPrintf("%d bytes of data sent successfully\n", msglen);
        } else {
            p[0] = false;
            mexErrMsgTxt("Failed to send message due to ZMQ error");
        }

        return;
    }
}
