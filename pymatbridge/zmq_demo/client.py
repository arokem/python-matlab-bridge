import zmq, json, bson
import numpy as np

# Please uncomment the decorator when profiling
# @profile
def run_client():
    # Initialize client
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:55555")

    # Generate a 72MB random array
    array = np.random.random_sample((2,2)).tolist()
    argument = {'val':array}

    # Send message and wait for a response
    message_out = json.dumps(argument)
    socket.send(message_out)
    print "Waiting for a message back"
    message_in = socket.recv()
    print "Got a message"
    print message_in
#    result = json.loads(message_in)['res']

    # Check if the received message matches the original one
    if result == np.sum(array):
        print "Success"
        print "Sum of orriginal array: ", np.sum(array)
        print "Sum calculated by the server: ", result

run_client()
