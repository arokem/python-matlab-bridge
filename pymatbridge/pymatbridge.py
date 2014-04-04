"""
pymatbridge
===========

This is a module for communicating and running

Part of Python-MATLAB-bridge, Max Jaderberg 2012

This is a modified version using ZMQ, Haoxing Zhang Jan.2014
"""

import numpy as np
import os, time
import zmq
import subprocess
import platform
import sys

import json

# JSON encoder extension to handle complex numbers
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, complex):
            return {'real':obj.real, 'imag':obj.imag}
        # Handle the default case
        return json.JSONEncoder.default(self, obj)

# JSON decoder for complex numbers
def as_complex(dct):
    if 'real' in dct and 'imag' in dct:
        return complex(dct['real'], dct['imag'])
    return dct


MATLAB_FOLDER = '%s/matlab' % os.path.realpath(os.path.dirname(__file__))

# Start a Matlab server and bind it to a ZMQ socket(TCP/IPC)
def _run_matlab_server(matlab_bin, matlab_socket_addr, matlab_log, matlab_id, matlab_startup_options):
    command = matlab_bin
    command += ' %s ' % matlab_startup_options
    command += ' -r "'
    command += "addpath(genpath("
    command += "'%s'" % MATLAB_FOLDER
    command += ')), matlabserver(\'%s\'),exit"' % matlab_socket_addr

    if matlab_log:
        command += ' -logfile ./pymatbridge/logs/matlablog_%s.txt > ./pymatbridge/logs/bashlog_%s.txt' % (matlab_id, matlab_id)

    subprocess.Popen(command, shell = True, stdin=subprocess.PIPE)

    return True


class Matlab(object):
    """
    A class for communicating with a matlab session
    """

    def __init__(self, matlab='matlab', socket_addr=None,
                 id='python-matlab-bridge', log=False, maxtime=60,
                 platform=None, startup_options=None):
        """
        Initialize this thing.

        Parameters
        ----------

        matlab : str
            A string that woul start matlab at the terminal. Per default, this
            is set to 'matlab', so that you can alias in your bash setup

        socket_addr : str
            A string that represents a valid ZMQ socket address, such as
            "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:55555", etc.

        id : str
            An identifier for this instance of the pymatbridge

        log : bool
            Whether to save a log file in some known location.

        maxtime : float
           The maximal time to wait for a response from matlab (optional,
           Default is 10 sec)

        platform : string
           The OS of the machine on which this is running. Per default this
           will be taken from sys.platform.

        """
        # Setup internal state variables
        self.started = False
        self.running = False
        self.matlab = matlab
        self.socket_addr = socket_addr

        self.id = id
        self.log = log
        self.maxtime = maxtime

        if platform is None:
            self.platform = sys.platform
        else:
            self.platform = platform

        if self.socket_addr is None:  # use the default
            self.socket_addr = "tcp://127.0.0.1:55555" if self.platform == "win32" else "ipc:///tmp/pymatbridge"

        if startup_options:
            self.startup_options = startup_options
        elif self.platform == 'win32':
            self.startup_options = ' -automation -noFigureWindows'
        else:
            self.startup_options = ' -nodesktop -nodisplay'

        self.context = None
        self.socket = None

    # Start server/client session and make the connection
    def start(self):
        # Start the MATLAB server in a new process
        print "Starting MATLAB on ZMQ socket %s" % (self.socket_addr)
        print "Send 'exit' command to kill the server"
        _run_matlab_server(self.matlab, self.socket_addr, self.log, self.id, self.startup_options)

        # Start the client
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.socket_addr)

        self.started = True

        # Test if connection is established
        if (self.is_connected()):
            print "MATLAB started and connected!"
            return True
        else:
            print "MATLAB failed to start"
            return False


    # Stop the Matlab server
    def stop(self):
        req = json.dumps(dict(cmd="exit"), cls=ComplexEncoder)
        self.socket.send(req)
        resp = self.socket.recv_string()

        # Matlab should respond with "exit" if successful
        if resp == "exit":
            print "MATLAB closed"

        self.started = False
        return True

    # To test if the client can talk to the server
    def is_connected(self):
        if not self.started:
            time.sleep(2)
            return False

        req = json.dumps(dict(cmd="connect"), cls=ComplexEncoder)
        self.socket.send(req)

        start_time = time.time()
        while(True):
            try:
                resp = self.socket.recv_string(flags=zmq.NOBLOCK)
                if resp == "connected":
                    return True
                else:
                    return False
            except zmq.ZMQError:
                np.disp(".", linefeed=False)
                time.sleep(1)
                if (time.time() - start_time > self.maxtime) :
                    print "Matlab session timed out after %d seconds" % (self.maxtime)
                    return False


    def is_function_processor_working(self):
        result = self.run_func('%s/test_functions/test_sum.m' % MATLAB_FOLDER, {'echo': 'Matlab: Function processor is working!'})
        if result['success'] == 'true':
            return True
        else:
            return False


    # Run a function in Matlab and return the result
    def run_func(self, func_path, func_args=None, maxtime=None):
        if self.running:
            time.sleep(0.05)

        req = dict(cmd="run_function")
        req['func_path'] = func_path
        req['func_args'] = func_args

        req = json.dumps(req, cls=ComplexEncoder)
        self.socket.send(req)
        resp = self.socket.recv_string()
        resp = json.loads(resp, object_hook=as_complex)

        return resp

    # Run some code in Matlab command line provide by a string
    def run_code(self, code, maxtime=None):
        if self.running:
            time.sleep(0.05)

        req = dict(cmd="run_code")
        req['code'] = code
        req = json.dumps(req, cls=ComplexEncoder)
        self.socket.send(req)
        resp = self.socket.recv_string()
        resp = json.loads(resp, object_hook=as_complex)

        return resp

    def get_variable(self, varname, maxtime=None):
        if self.running:
            time.sleep(0.05)

        req = dict(cmd="get_var")
        req['varname'] = varname
        req = json.dumps(req, cls=ComplexEncoder)
        self.socket.send(req)
        resp = self.socket.recv_string()
        resp = json.loads(resp, object_hook=as_complex)

        return resp['var']

