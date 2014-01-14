import numpy as np
import os, json, time, socket
import zmq
from multiprocessing import Process
import subprocess
import platform
import sys

MATLAB_FOLDER = '%s/matlab' % os.path.realpath(os.path.dirname(__file__))

# Start the Matlab server and bind it to a socket
def _run_matlab_server(matlab_bin, matlab_socket_addr, matlab_startup_options):
    command = matlab_bin
    command += ' %s ' % matlab_startup_options
    command += ' -r "'
    command += "addpath(genpath("
    command += "'%s'" % MATLAB_FOLDER
    command += ')), matlabserver(\'%s\'),exit"' % matlab_socket_addr

    subprocess.Popen(command, shell=True)

    return True


class Matlab(object):

    def __init__(self, matlab='matlab', socket_addr='ipc:///tmp/pymatbridge', startup_options=None, platform=None):
        # These are the matlab functions that post requests to the webserever
        # through the methods of this class:
        self.feval = 'web_feval.m'
        self.eval = 'web_eval.m'
        self.get_var = 'web_get_variable.m'
        self.matlab = matlab
        self.socket_addr = socket_addr
        self.context = None
        self.socket = None

        if platform is None:
            self.platform = sys.platform
        else:
            self.platform = platform

        if startup_options:
            self.startup_options = startup_options
        elif self.platform == 'Windows':
            self.startup_options = ' -automation -noFigureWindows'
        else:
            self.startup_options = ' -nodesktop -nodisplay'


    def start(self):
        # Start the MATLAB server
        print "Starting MATLAB on %s" % (self.socket_addr)
        print "Send 'exit' to shut down the server"

        _run_matlab_server(self.matlab, self.socket_addr, self.startup_options)

        # Start the client
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.socket_addr)

        # Test if connection is established
        while not self.is_connected():
            np.disp(".", linefeed=False)
            time.sleep(1)

        print "MATLAB started and connected!"

        return True


    def stop(self):
        # Stop the MATLAB server
        req = json.dumps(dict(cmd="exit"))
        self.socket.send(req)
        resp = self.socket.recv_string()

        if resp == "exit":
            print "MATLAB closed"

        return True


    def is_connected(self):
        req = json.dumps(dict(cmd="connect"))
        self.socket.send(req)
        resp = self.socket.recv_string()

        if resp == "connected":
            return True
        else:
            return False

    def is_function_processor_working(self):
        try:
            result = self.run_func('%s/test_functions/test_sum.m' % MATLAB_FOLDER, {'echo': 'Matlab: Function processor is working!'})
            if result['success'] == 'true':
                return True
        except urllib2.URLError:
            pass
        return False


    def run_func(self, func_path, func_args=None, maxtime=None):
        req = dict(cmd="run_function")
        req['func_path'] = func_path
        req['func_args'] = func_args

        req = json.dumps(req)
        self.socket.send(req)
        resp = self.socket.recv_string()
        resp = json.loads(resp)

        return resp['result']


    def run_code(self, code, maxtime=None):
        """

        Run a piece of code provided as a string

        """
        if self.running:
            time.sleep(0.05)

        if maxtime:
            result = self._open_page(self.eval, dict(code=code), maxtime)
        else:
            result = self._open_page(self.eval, dict(code=code), self.maxtime)

        return result

    def get_variable(self, varname, maxtime=None):
        if self.running:
            time.sleep(0.05)

        if maxtime:
            result = self._open_page(self.get_var, dict(varname=varname),
                                     maxtime)
        else:
            result = self._open_page(self.get_var, dict(varname=varname),
                                     self.maxtime)

        return result['var']


    def _open_page(self, page_name, arguments={}, timeout=10):
        self.running = True
        page = urllib2.urlopen('%s/%s' % (self.server, page_name),
                               urllib.urlencode(arguments),
                               timeout)

        self.running = False
        read_page = page.read()
        # Deal with escape characters: json needs an additional '\':
        # Kill backspaces (why does Matlab even put these there!?):
        read_page = read_page.replace("\x08", "")
        if self.platform == 'Windows':
            # Matlab strings containing \ for the dir names on windows:
            read_page = read_page.replace("\\", "\\\\")

        # Keep new-lines:
        read_page = read_page.replace("\n","\\n")
        return json.loads(read_page)


