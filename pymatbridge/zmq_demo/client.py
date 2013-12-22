import zmq, json, bson
import numpy as np

# Please uncomment the decorator when profiling
# @profile
def run_client():
    # Initialize client
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("ipc:///tmp/ipctest")

    # Generate a 72MB random array
    array = np.random.random_sample((3000,3000)).tolist()
    argument = {'val':array}

    # Send message and wait for a response
    message_out = json.dumps(argument)
    socket.send(message_out)
    message_in = socket.recv()
    result = json.loads(message_in)['res']

    # Check if the received message matches the original one
    if result == np.sum(array):
        print "Success"
        print "Sum of orriginal array: ", np.sum(array)
        print "Sum calculated by the server: ", result

run_client()
