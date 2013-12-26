import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("ipc:///tmp/ipctest")

for i in range(0,10):
    print "Sending request %d", i
    socket.send("Hello")
    response = socket.recv_string()
    print "Got response %d: %s" % (i, response)


