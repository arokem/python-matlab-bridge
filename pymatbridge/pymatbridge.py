"""Main module for running and communicating with Matlab subprocess

pymatbridge.py provides Matlab, the main class used to communicate
with the Matlab executable. Each instance starts and manages its
own Matlab subprocess.

"""
from __future__ import print_function
import collections
import functools
import json
import numpy as np
import os
import platform
import subprocess
import sys
import time
import types
import weakref
import zmq
try:
    # Python 2
    basestring
    DEVNULL = open(os.devnull, 'w')
except:
    # Python 3
    basestring = str
    DEVNULL = subprocess.DEVNULL


# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def chain(*iterables):
    """Yield elements from each iterable in order

    Make an iterator that returns elements from the first iterable until
    it is exhausted, then proceeds to the next iterable, until all of the
    iterables are exhausted. Unlike itertools.chain, strings are not treated
    as iterable, and thus not expanded into characters:
    chain([1, 2, 3, 4], 'string') --> 1, 2, 3, 4, 'string'

    Returns:
        generator: A generator which yields items from the iterables

    """
    for iterable in iterables:
        if not isinstance(iterable, collections.Iterable) or isinstance(iterable, basestring):
            yield iterable
        else:
            for item in iterable:
                yield item


class AttributeDict(dict):
    """A dictionary with attribute-like access

    Values within an AttributeDict can be accessed either via
    d[key] or d.key.
    See: http://stackoverflow.com/a/14620633

    """
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


# ----------------------------------------------------------------------------
# JSON EXTENSION
# ----------------------------------------------------------------------------
class MatlabEncoder(json.JSONEncoder):
    """A JSON extension for encoding numpy arrays to Matlab format

    Numpy arrays are converted to nested lists. Complex numbers
    (either standalone or scalars within an array) are converted to JSON
    objects.
    complex --> {'real': complex.real, 'imag': complex.imag}
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            ordering = range(0, obj.ndim)
            ordering[0:2] = ordering[1::-1]
            return np.transpose(obj, axes=ordering[::-1]).tolist()
        if isinstance(obj, complex):
            return {'real':obj.real, 'imag':obj.imag}
        # Handle the default case
        return super(MatlabEncoder, self).default(obj)


class MatlabDecoder(json.JSONDecoder):
    """A JSON extension for decoding Matlab arrays into numpy arrays

    The default JSON decoder is called first, then elements within the
    resulting object tree are greedily marshalled to numpy arrays. If this
    fails, the function recurses into
    """
    def __init__(self, encoding='UTF-8', **kwargs):
        # register the complex object decoder with the super class
        kwargs['object_hook'] = self.decode_complex
        # allowable scalar types we can coerce to (not strings or objects)
        super(MatlabDecoder, self).__init__(encoding=encoding, **kwargs)

    def decode(self, s):
        # decode the string using the default decoder first
        tree = super(MatlabDecoder, self).decode(s)
        # recursively attempt to build numpy arrays (top-down)
        return self.coerce_to_numpy(tree)

    def decode_complex(self, d):
        try:
            return complex(d['real'], d['imag'])
        except KeyError:
            return d

    def coerce_to_numpy(self, tree):
        """Greedily attempt to coerce an object into a numeric numpy"""
        if isinstance(tree, dict):
            return dict((key, self.coerce_to_numpy(val)) for key, val in tree.items())
        if isinstance(tree, list):
            array = np.array(tree)
            if isinstance(array.dtype.type(), (bool, int, float, complex)):
                ordering = range(0, array.ndim)
                ordering[-2:] = ordering[:-3:-1]
                return np.transpose(array, axes=ordering[::-1])
            else:
                return [self.coerce_to_numpy(item) for item in tree]
        return tree


# ----------------------------------------------------------------------------
# MATLAB
# ----------------------------------------------------------------------------
class Matlab(object):
    def __init__(self, matlab='matlab', socket_addr=None,
                 id='python-matlab-bridge', log=False, timeout=30,
                 platform=None, startup_options=None):
        """Execute functions in a Matlab subprocess via Python

        Matlab provides a pythonic interface for accessing functions in Matlab.
        It works by starting a Matlab subprocess and establishing a connection
        to it using ZMQ. Function calls are serialized and executed remotely.

        Keyword Args:
            matlab (str): A string to the Matlab executable. This defaults
                to 'matlab', assuming the executable is on your PATH
            socket_addr (str): A string the represents a valid ZMQ socket
                address, such as "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:5555"
            id (str): An identifier for this instance of the pymatbridge
            log (bool): Log status and error messages
            timeout: The maximum time to wait for a response from the Matlab
                process before timing out (default 30 seconds)
            platform (str): The OS of the machine running Matlab. By default
                this is determined automatically from sys.platform
            startup_options (list): A list of switches that should be passed
                to the Matlab subprocess at startup. By default, switches are
                passed to disable the graphical session. For a full list of
                available switches see:
                Windows: http://www.mathworks.com.au/help/matlab/ref/matlabwindows.html
                UNIX: http://www.mathworks.com.au/help/matlab/ref/matlabunix.html

        """
        self.MATLAB_FOLDER = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'matlab')

        # Setup internal state variables
        self.started = False
        self.matlab = matlab
        self.socket_addr = socket_addr
        self.id = id
        self.log = log
        self.timeout = timeout

        # determine the platform-specific options
        self.platform = platform if platform else sys.platform
        if self.platform == 'win32':
            default_socket_addr = "tcp://127.0.0.1:55555"
            default_options     = ['-automation', '-nofigureWindows']
        else:
            default_socket_addr = "ipc:///tmp/pymatbridge"
            default_options     = ['-nodesktop', '-nodisplay']

        self.socket_addr = socket_addr if socket_addr else default_socket_addr
        self.startup_options = startup_options if startup_options else default_options

        # initialize the ZMQ socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

        # auto-generate some useful matlab builtins
        self.bind_method('exist',   unconditionally=True)
        self.bind_method('addpath', unconditionally=True)
        self.bind_method('eval',    unconditionally=True)
        self.bind_method('help',    unconditionally=True)
        self.bind_method('license', unconditionally=True)
        self.bind_method('run',     unconditionally=True)
        self.bind_method('version', unconditionally=True)

    def __del__(self):
        """Forcibly cleanup resources

        The user should always call Matlab.stop to gracefully shutdown the Matlab
        process before Matlab leaves scope, but in case they don't, attempt
        to cleanup so we don't leave an orphaned process lying around.

        """
        self.stop()

    def start(self):
        """Start a new Matlab subprocess and attempt to connect to it via ZMQ

        Raises:
            RuntimeError: If Matlab is already running, or failed to start

        """
        if self.started:
            raise RuntimeError('Matlab is already running')

        # build the command
        command = chain(
          self.matlab,
          self.startup_options,
          '-r',
          "\"addpath(genpath('%s')),matlabserver('%s'),exit\"" % (self.MATLAB_FOLDER, self.socket_addr)
        )

        command = ' '.join(command)
        print('Starting Matlab subprocess', end='')
        self.matlab_process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=DEVNULL)

        # Start the client
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.socket_addr)
        self.started = True

        # Test if connection is established
        if (self.is_connected()):
            print('started')
        else:
            self.started = False
            raise RuntimeError('Matlab failed to start')

    def stop(self, timeout=1):
        """Stop the Matlab subprocess

        Attempt to gracefully shutdown the Matlab subprocess. If it fails to
        stop within the timeout period, terminate it forcefully.

        Args:
            timeout: Time in seconds before SIGKILL is sent

        """
        if not self.started:
            return

        req = json.dumps({'cmd': 'exit'})
        try:
            # the user might be stopping Matlab because the socket is in a bad state
            self.socket.send(req)
        except:
            pass

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.matlab_process.poll() is not None:
                break
            time.sleep(0.1)
        else:
            self.matlab_process.kill()

        # finalize
        self.socket.close()
        self.started = False

    def restart(self):
        """Restart the Matlab subprocess if the state becomes bad

        Aliases the following command:
            >> matlab.stop()
            >> matlab.start()

        """
        self.stop()
        self.start()

    def is_connected(self):
        """Test if the client can talk to the server

        Raises:
            RuntimeError: If there is no running Matlab subprocess to connect to

        Returns:
            bool: True if the Matlab subprocess ZMQ server can be contacted,
                  False, otherwise

        """
        if not self.started:
            raise RuntimeError('No running Matlab subprocess to connect to')

        req = json.dumps({'cmd': 'ping'})
        self.socket.send(req)

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            time.sleep(0.5)
            try:
                self.socket.recv_string(flags=zmq.NOBLOCK)
                return True
            except zmq.ZMQError:
                print('.', end='')
                sys.stdout.flush()

        print('failed to connect to Matlab after %d seconds' % self.timeout)
        return False

    def is_function_processor_working(self):
        """Check whether the Matlab subprocess can evaluate functions

        First check whether the Python client can talk to the Matlab
        server, then if the server is in a state where it can successfully
        evaluate a function

        Raises:
            RuntimeError: If there is no running Matlab subprocess to connect to

        Returns:
            bool: True if Matlab can evaluate a function, False otherwise

        """
        if not self.is_connected():
            return False

        try:
            self.abs(2435)
            return True
        except:
            return False

    def execute_in_matlab(self, req):
        """Execute a request in the Matlab subprocess

        Args:
            req (dict): A dictionary containing the request to evaluate in
                Matlab. The request should contain the 'cmd' key, and the
                corresponding command recognized by matlabserver.m, as well
                as any arguments required by that command

        Returns:
            resp (dict): A dictionary containing the response from the Matlab
                server containing the keys 'success', 'result', and 'message'

        Raises:
            RuntimeError: If the 'success' field of the resp object is False,
                then an exception is raised with the value of the 'result'
                field which will contain the identifier of the exception
                raised in Matlab, and the 'message' field, which will contain
                the reason for the exception

        """
        # send the request
        req = json.dumps(req, cls=MatlabEncoder)
        self.socket.send(req)

        # receive the response
        resp = self.socket.recv_string()
        resp = AttributeDict(json.loads(resp, cls=MatlabDecoder))
        if not resp.success:
            raise RuntimeError(resp.result +': '+ resp.message)
        return resp

    def __getattr__(self, name):
        return self.bind_method(name)
    def bind_method(self, name, unconditionally=False):
        """Generate a Matlab function and bind it to the instance

        This is where the magic happens. When an unknown attribute of the
        Matlab class is requested, it is assumed to be a call to a
        Matlab function, and is generated and bound to the instance.

        This works because getattr() falls back to __getattr__ only if no
        attributes of the requested name can be found through normal
        routes (__getattribute__, __dict__, class tree).

        bind_method first checks whether the requested name is a callable
        Matlab function before generating a binding.

        Args:
            name (str): The name of the Matlab function to call
                e.g. 'sqrt', 'sum', 'svd', etc
            unconditionally (bool): Bind the method without performing
                checks. Used to bootstrap methods that are required and
                know to exist

        Returns:
            Method: a reference to a newly bound Method instance if the
                requested name is determined to be a callable function

        Raises:
            AttributeError: if the requested name is not a callable
                Matlab function

        """
        # TODO: This does not work if the function is a mex function inside a folder of the same name
        if not unconditionally and not self.exist(name):
            raise AttributeError("'Matlab' object has no attribute '%s'" % name)

        # create a new method instance
        method_instance = Method(weakref.ref(self), name)
        method_instance.__name__ = name

        # bind to the Matlab instance with a weakref (to avoid circular references)
        setattr(self, name, types.MethodType(method_instance, weakref.ref(self), Matlab))
        return getattr(self, name)


    def run_func(self, func_path, func_args=None, maxtime=None):
        path, filename = os.path.split(func_path)
        func, ext = filename.split('.')

        self.addpath(path)

    def run_code(self, code, maxtime=None):
        try:
            return {'result': self.eval(code), 'success': 'true', 'message': ''}
        except RuntimeError as e:
            return {'result': '', 'success': 'false', 'message': e}

    def get_variable(self, varname, maxtime=None):
        return self.evalin('base',varname)


# ----------------------------------------------------------------------------
# MATLAB METHOD
# ----------------------------------------------------------------------------
class Method(object):

    def __init__(self, parent, name):
        """An object representing a Matlab function

        Methods are dynamically bound to instances of Matlab objects and
        represent a callable function in the Matlab subprocess.

        Args:
            parent: A reference to the parent (Matlab instance) to which the
                Method is being bound
            name: The name of the Matlab function this represents

        """
        self.name = name
        self._parent = parent
        self.doc = None

    def __call__(self, unused_parent_weakref, *args, **kwargs):
        """Call a function with the supplied arguments in the Matlab subprocess

        Args:
            The *args parameter is unpacked and forwarded verbatim to Matlab.
            It contains arguments in the order that they would appear in a
            native function call.

        Keyword Args:
            Keyword arguments are passed to Matlab in the form [key, val] so
            that matlab.plot(x, y, '--', LineWidth=2) would be translated into
            plot(x, y, '--', 'LineWidth', 2)

            nout (int): The number of arguments to output. By default this is
                1 for functions that return 1 or more values, and 0 for
                functions that return no values. This is useful for functions
                that change their behvaiour depending on the number of inputs:
                U, S, V = matlab.svd(A, nout=3)

        """
        # parse out number of output arguments
        nout  = kwargs.pop('nout', None)

        # convert keyword arguments to arguments
        args += tuple(item for pair in zip(kwargs.keys(), kwargs.values()) for item in pair)

        # build request
        req   = {'cmd': 'call', 'func': self.name, 'args': args, 'nout': nout}
        resp  = self.parent.execute_in_matlab(req)

        # return the result
        return resp.get('result', None)

    @property
    def parent(self):
        """Get the actual parent from the stored weakref

        The parent (Matlab instance) is stored as a weak reference
        to eliminate circular references from dynamically binding Methods
        to Matlab.

        """
        parent = self._parent()
        if parent is None:
            raise AttributeError('Stale reference to attribute of non-existent Matlab object')
        return parent

    @property
    def __doc__(self):
        """Fetch the docstring from Matlab

        Get the documentation for a Matlab function by calling Matlab's builtin
        help() then returning it as the Python docstring. The result is cached
        so Matlab is only ever polled on the first request

        """
        if self.doc is None:
            self.doc = self.parent.help(self.name)
        return self.doc
