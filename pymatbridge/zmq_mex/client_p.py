import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("ipc:///tmp/zmqmatlab")

for i in range(0,10):
    print "Sending: Hello #%d" % (i)
    socket.send("Hello #%d" % (i))
    response = socket.recv_string()
    print "Received: %s" % (response)


