import zmq, json
import numpy as np

def run_server():
    # Initializing server
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("ipc:///tmp/ipctest")

    while True:
        message_in = socket.recv()
        print "Request received"
    # Retrieve array from the message
        argument = json.loads(message_in)
        array = argument['val']
    # Calculate the sum of array elements
        sum_array = np.sum(array)
        result = {'res':sum_array}
        message_out = json.dumps(result)
    # Send out reply
        socket.send(message_out)
        print "Response sent"


run_server()
