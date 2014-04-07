"""
pymatbridge
===========

This is a module for communicating and running

Part of Python-MATLAB-bridge, Max Jaderberg 2012

This is a modified version using ZMQ, Haoxing Zhang Jan.2014
"""
from __future__ import print_function
import collections
import functools
import json
import os
import platform
import subprocess
import sys
import time
import types
import weakref
import zmq
try:
  basestring
  DEVNULL = open(os.devnull, 'w')
except:
  basestring = str
  DEVNULL = subprocess.DEVNULL

# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def chain(*iterables):
    for iterable in iterables:
        if not isinstance(iterable, collections.Iterable) or isinstance(iterable, basestring):
            yield iterable
        else:
            for item in iterable:
                yield item


# ----------------------------------------------------------------------------
# JSON EXTENSION
# ----------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------
# MATLAB
# ----------------------------------------------------------------------------
MATLAB_FOLDER = '%s/matlab' % os.path.realpath(os.path.dirname(__file__))

class Matlab(object):
    """
    A class for communicating with a matlab session
    """

    def __init__(self, matlab='matlab', socket_addr=None,
                 id='python-matlab-bridge', log=False, maxtime=30,
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
        self.blacklist = set()

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

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

        # generate some useful matlab builtins
        getattr(self, 'addpath')
        getattr(self, 'eval')
        getattr(self, 'help')
        getattr(self, 'license')
        getattr(self, 'run')
        getattr(self, 'run')
        getattr(self, 'version')

    def __del__(self):
        self.socket.close()
        try:
          self.matlab_process.terminate()
        except:
          pass

    # ------------------------------------------------------------------------
    # START/STOP SERVER
    # ------------------------------------------------------------------------
    # Start server/client session and make the connection
    def start(self):
        # Start the MATLAB server in a new process
        command = chain(
          self.matlab,
          self.startup_options,
          '-r',
          "\"addpath(genpath('%s')),matlabserver('%s'),exit\"" % (MATLAB_FOLDER, self.socket_addr)
        )

        command = ' '.join(command)
        print('Starting Matlab subprocess', end='')
        self.matlab_process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=DEVNULL)

        # Start the client
        self.socket.connect(self.socket_addr)
        self.started = True

        # Test if connection is established
        if (self.is_connected()):
            print('ready')
        else:
            raise RuntimeError('Matlab failed to start')


    # Stop the Matlab server
    def stop(self):
        req = json.dumps({'cmd': 'exit'}, cls=ComplexEncoder)
        self.socket.send(req)
        resp = self.socket.recv_string()

        # Matlab should respond with "exit" if successful
        if resp == "exit":
            print("Matlab subprocess stopped")
        self.started = False

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
                print('.', end='')
                sys.stdout.flush()
                time.sleep(1)
                if (time.time() - start_time > self.maxtime) :
                    print('failed to connect to Matlab after %d seconds' % self.maxtime)
                    return False


    def is_function_processor_working(self):
        result = self.run_func('%s/test_functions/test_sum.m' % MATLAB_FOLDER, {'echo': 'Matlab: Function processor is working!'})
        if result['success'] == 'true':
            return True
        else:
            return False

    def _execute(self, req):
        req = json.dumps(req, cls=ComplexEncoder)
        self.socket.send(req)
        resp = self.socket.recv_string()
        resp = json.loads(resp, object_hook=as_complex)

        return resp


    # ------------------------------------------------------------------------
    # PYTHONIC API
    # ------------------------------------------------------------------------
    def __getattr__(self, name):
        if name in self.blacklist:
            raise AttributeError(attribute_msg.format(name))
        method_instance = Method(self, name)
        method_instance.__name__ = name + ' (unverified)'
        setattr(self, name, types.MethodType(method_instance, weakref.ref(self), Matlab))
        return getattr(self, name)

    def get_variable(self, varname, timeout=None):
        req = {
            'cmd': 'get_var',
            'varname': varname,
        }
        resp = self._execute(req)
        if not resp['success']:
            raise RuntimeError(resp['result'] +': '+ resp['message'])
        return resp['result']

    def clear_blacklist(self):
        self.blacklist = set()


# ----------------------------------------------------------------------------
# MATLAB METHOD
# ----------------------------------------------------------------------------
attribute_msg = "attribute '{0}' does not correspond to a Matlab function and was blacklisted"

class Method(object):

    def __init__(self, parent, name):
        self.name = name
        self.doc = None

    def __call__(self, parent, *args, **kwargs):
        nout  = kwargs.pop('nout', None)
        args += tuple(item for pair in zip(kwargs.keys(), kwargs.values()) for item in pair)
        req = {
            'cmd': 'call',
            'func': self.name,
            'args': args
        }
        if nout:
            req['nout'] = nout
        resp = parent()._execute(req)
        if not resp['success']:
            if resp['result'] == 'MATLAB:UndefinedFunction':
                parent().blacklist.add(self.name)
                delattr(parent(), self.name)
                raise AttributeError(attribute_msg.format(self.name))
            raise RuntimeError(resp['result'] +': '+ resp['message'])
        else:
            self.__name__ = self.name + ' (verified)'
        return resp['result']

    @property
    def __doc__(self, parent):
        if not self.doc:
            self.doc = parent().help(self.name)
        return self.doc
