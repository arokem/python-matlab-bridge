clear;clc;

% This server sends back whatever it gets
init_result = zmq_server('initialize');
while(1)
    msg_in = zmq_server('listen');
    status = zmq_server('respond', msg_in);
end