import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("ipc:///tmp/ipctest")

while True:
    message_in = socket.recv()
    print "Request received: ", message_in
    # Send out reply
    socket.send("World")
    print "Response sent"

