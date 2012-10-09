"""
pymatbridge
===========

This is a module for communicating and running 

Part of Python-MATLAB-bridge, Max Jaderberg 2012 

"""

import numpy as np
from httplib import BadStatusLine
import urllib2, urllib, os, json, time, socket
from multiprocessing import Process

MATLAB_FOLDER = '%s/matlab' % os.path.realpath(os.path.dirname(__file__))

class Matlab(object):
    """
    A class for communicating with a matlab session
    """        
    running = False
    matlab = None
    host = None
    port = None
    server = None
    id = None
    server_process = Process()

    def __init__(self, matlab='matlab', host='localhost', port=None,
                 id='python-matlab-bridge', log=False):
        """
        Initialize this thing.

        Parameters
        ----------

        matlab : str
            A string that woul start matlab at the terminal. Per default, this
            is set to 'matlab', so that you can alias in your bash setup

        host : str
            If you want something else than 'localhost', blame yourself

        port : integer
            This is the number of the port. The default (None), gets a random
            free port

        id : str
            An identifier for this instance of the pymatbridge

        log : bool
            Whether to save a log file in some known location.
            
        """

        # These are the matlab functions that post requests to the webserever
        # through the methods of this class:
        self.feval = 'web_feval.m'
        self.eval = 'web_eval.m'
        self.get_var = 'web_get_variable.m'

        self.matlab = matlab
        self.host = host
        if self.port is None:
            sock = socket.socket()
            sock.bind(('', 0))
            port = sock.getsockname()[1]
        self.port = port
        self.server = 'http://%s:%s' % (self.host, str(self.port))
        self.id = id
        self.log = log

    def start(self):
        def _run_matlab_server():
            cmd_str = '%s -nodesktop -nosplash -nodisplay -r "cd pymatbridge/matlab,webserver(%s),exit"'%(self.matlab, self.port)

            if self.log:
                cmd_str += ' -logfile ./pymatbridge/logs/matlablog_%s.txt > ./pymatbridge/logs/bashlog_%s.txt' % (self.id, self.id)

            os.system(cmd_str)
            return True

        # Start the MATLAB server
        print "Starting MATLAB on http://%s:%s" % (self.host, str(self.port))
        self.server_process = Process(target=_run_matlab_server)
        self.server_process.daemon = True
        self.server_process.start()
        while not self.is_connected():
            np.disp(".", linefeed=False)
            time.sleep(1)
        print "MATLAB started and connected!"
        return True


    def stop(self):
        # Stop the MATLAB server
        try:
            try:
                resp = self._open_page('exit_server.m', {'id': self.id})
            except BadStatusLine:
                pass
        except urllib2.URLError:
            pass
        print "MATLAB closed"
        return True

    def is_connected(self):
        try:
            resp = self._open_page('test_connect.m', {'id': self.id})
            if resp['message']:
                return True
        except urllib2.URLError:
            pass
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
        if self.running:
            time.sleep(0.05)
        page_args = {
            'func_path': func_path,
        }
        if func_args:
            page_args['arguments'] = json.dumps(func_args)
        if maxtime:
            result = self._open_page(self.feval, page_args, maxtime)
        else:
            result = self._open_page(self.feval, page_args)
        return result


    def run_code(self, code, maxtime=None):
        """

        Run a piece of code provided as a string

        """
        if self.running:
            time.sleep(0.05)
            
        if maxtime:
            result = self._open_page(self.eval, dict(code=code), maxtime)
        else:
            result = self._open_page(self.eval, dict(code=code))

        return result

    def get_variable(self, varname, maxtime=None):
        if self.running:
            time.sleep(0.05)
            
        if maxtime:
            result = self._open_page(self.get_var, dict(varname=varname),
                                     maxtime)
        else:
            result = self._open_page(self.get_var, dict(varname=varname))

        return result['var']
        
        
    def _open_page(self, page_name, arguments={}, timeout=10):
        self.running = True
        page = urllib2.urlopen('%s/%s' % (self.server, page_name),
                               urllib.urlencode(arguments),
                               timeout)
        
        self.running = False
        read_page = page.read()
        # Deal with escape characters: json needs an additional '\': 
        return json.loads(read_page.replace("\n","\\n"))


