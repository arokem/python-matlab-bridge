"""
pymatbridge
===========

This is a module for communicating and running Matlab from within python

Example
-------

>>> import pymatbridge
>>> m = pymatbridge.Matlab()
>>> m.start()
Starting MATLAB on ZMQ socket ipc:///tmp/pymatbridge
Send 'exit' command to kill the server
.MATLAB started and connected!
True
>>> m.run_code('a=1;')
{'content': {'stdout': '', 'datadir': '/private/tmp/MatlabData/', 'code': 'a=1;', 'figures': []}, 'success': True}
>>> m.get_variable('a')
1

"""

import atexit
import os
import time
import base64
import zmq
import subprocess
import sys
import json
import types
import weakref
import random
import logging
from uuid import uuid4

from numpy import ndarray, generic, float64, frombuffer, asfortranarray

try:
    from scipy.sparse import spmatrix
except ImportError:
    class spmatrix:
        pass


def encode_ndarray(obj):
    """Write a numpy array and its shape to base64 buffers"""
    shape = obj.shape
    if len(shape) == 1:
        shape = (1, obj.shape[0])
    if obj.flags.c_contiguous:
        obj = obj.T
    elif not obj.flags.f_contiguous:
        obj = asfortranarray(obj.T)
    else:
        obj = obj.T
    try:
        data = obj.astype(float64).tobytes()
    except AttributeError:
        data = obj.astype(float64).tostring()

    data = base64.b64encode(data).decode('utf-8')
    return data, shape


# JSON encoder extension to handle complex numbers and numpy arrays
class PymatEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ndarray) and obj.dtype.kind in 'uif':
            data, shape = encode_ndarray(obj)
            return {'ndarray': True, 'shape': shape, 'data': data}
        elif isinstance(obj, ndarray) and obj.dtype.kind == 'c':
            real, shape = encode_ndarray(obj.real.copy())
            imag, _ = encode_ndarray(obj.imag.copy())
            return {'ndarray': True, 'shape': shape,
                    'real': real, 'imag': imag}
        elif isinstance(obj, ndarray):
            return obj.tolist()
        elif isinstance(obj, complex):
            return {'real': obj.real, 'imag': obj.imag}
        elif isinstance(obj, generic):
            return obj.item()
        # Handle the default case
        return json.JSONEncoder.default(self, obj)


def decode_arr(data):
    """Extract a numpy array from a base64 buffer"""
    data = data.encode('utf-8')
    return frombuffer(base64.b64decode(data), float64)


# JSON decoder for arrays and complex numbers
def decode_pymat(dct):
    if 'ndarray' in dct and 'data' in dct:
        value = decode_arr(dct['data'])
        shape = dct['shape']
        if type(dct['shape']) is not list:
            shape = decode_arr(dct['shape']).astype(int)
        return value.reshape(shape, order='F')
    elif 'ndarray' in dct and 'imag' in dct:
        real = decode_arr(dct['real'])
        imag = decode_arr(dct['imag'])
        shape = decode_arr(dct['shape']).astype(int)
        data = real + 1j * imag
        return data.reshape(shape, order='F')
    elif 'real' in dct and 'imag' in dct:
        return complex(dct['real'], dct['imag'])
    return dct

MATLAB_FOLDER = '%s/matlab' % os.path.realpath(os.path.dirname(__file__))


class _Session(object):
    """
    A class for communicating with a MATLAB session. It provides the behavior
    common across different MATLAB implementations. You shouldn't instantiate
    this directly; rather, use the Matlab or Octave subclasses.
    """

    def __init__(self, executable=None, socket_addr=None,
                 id='python-matlab-bridge', log="", maxtime=15,
                 platform=None, startup_options=None,
                 loglevel=logging.WARNING):
        """
        Initialize this thing.

        Parameters
        ----------

        executable : str
            A string that would start the session at the terminal.

        socket_addr : str
            A string that represents a valid ZMQ socket address, such as
            "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:55555", etc. Default is
            to choose a random IPC file name, or a random socket (for TCP).

        id : str
            An identifier for this instance of the pymatbridge.

        log : str
            Location to log to, defaults to sys.stdout

        maxtime : float
           The maximal time to wait for a response from the session (optional,
           Default is 15 sec)

        platform : string
           The OS of the machine on which this is running. Per default this
           will be taken from sys.platform.

        startup_options : string
           Command line options to include in the executable's invocation.
           Optional; sensible defaults are used if this is not provided.
        """
        self.started = False
        self.executable = executable
        self.socket_addr = socket_addr
        self.id = id
        self.log = log
        self.maxtime = maxtime
        self.platform = platform if platform is not None else sys.platform
        self.startup_options = startup_options
        self.loglevel = loglevel
        if socket_addr is None:
            if self.platform == "win32":
                self.socket_addr = "tcp://127.0.0.1"
            else:
                self.socket_addr = "ipc:///tmp/pymatbridge-%s" % str(uuid4())
        else:
            self.socket_addr = socket_addr
        self.context = None
        self.socket = None
        self.logger = logging.getLogger(self.id)
        self.logger.setLevel(self.loglevel)
        if self.log:
            self.loghandler = logging.FileHandler(self.log)
        else:
            self.loghandler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.loghandler.setFormatter(formatter)
        self.logger.addHandler(self.loghandler)
        atexit.register(self.stop)

    def _program_name(self):  # pragma: no cover
        raise NotImplementedError

    def _execute_flag(self):  # pragma: no cover
        raise NotImplementedError

    def _run_server(self):
        code = "cd('{}'); matlabserver('{}', true);".format(
            MATLAB_FOLDER, self.socket_addr)
        command = '%s %s %s "%s"' % (self.executable, self.startup_options,
                                     self._execute_flag(), code)
        self.logger.info("Running: %s", command)
        subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)

    # Start server/client session and make the connection
    def start(self):
        # Setup socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        if self.platform == "win32":
            rndport = random.randrange(49152, 65536)
            self.socket_addr = self.socket_addr + ":%s"%rndport

        # Start the MATLAB server in a new process
        self.logger.info("Starting ZMQ socket %s", self.socket_addr)
        #self.logger.info("Run _Session.stop/separate to kill the server.")

        if self.executable:
            self.logger.info("Launching %s, sending ZMQ 'exit' will kill it.", \
                    self._program_name())
            self._run_server()

        # Start the client
        self.socket.connect(self.socket_addr)

        self.started = True

        # Test if connection is established
        if not self.is_connected():
            raise ValueError("%s failed to start" % self._program_name())

        self.logger.info("%s started and connected!", self._program_name())
        self.set_plot_settings()
        return self

    def _response(self, **kwargs):
        req = json.dumps(kwargs, cls=PymatEncoder)
        self.socket.send_string(req)
        resp = self.socket.recv_string()
        return resp

    # open desktop matlab and disconnect
    def separate(self):
        if not self.started:
            raise ValueError('Session not started, use start()')
        if self._response(cmd='separate') != 'exit':
            raise ValueError('Failed to separate from {}'.format(self._program_name))
        self.socket.close()
        self.context.term()
        self.logger.info("%s split off", self._program_name())
        self.started = False
        return True

    # Stop the Matlab server
    def stop(self):
        if not self.started:
            return True

        # Matlab should respond with "exit" if successful
        if self._response(cmd='exit') != "exit":
            raise ValueError("Failed to stop {}".format(self._program_name))
        self.socket.close()
        self.context.term()
        self.logger.info("%s closed", self._program_name())
        self.started = False
        return True

    # To test if the client can talk to the server
    def is_connected(self):
        if not self.started:
            return False

        req = json.dumps(dict(cmd="connect"), cls=PymatEncoder)
        self.socket.send_string(req)

        start_time = time.time()
        while True:
            try:
                resp = self.socket.recv_string(flags=zmq.NOBLOCK)
                return resp == "connected"
            except zmq.ZMQError:
                time.sleep(1)
                if time.time() - start_time > self.maxtime:
                    timed_out_str = "%s session timed out after %d seconds" \
                            % (self._program_name(), self.maxtime)
                    self.logger.warn(timed_out_str)
                    return False

    def is_function_processor_working(self):
        result = self.run_func('%s/usrprog/test_sum.m' % MATLAB_FOLDER,
                {'echo': '%s: Function processor is working!' % self._program_name()})
        return result['success']

    def _json_response(self, **kwargs):
        return json.loads(self._response(**kwargs), object_hook=decode_pymat)

    def run_func(self, func_path, *func_args, **kwargs):
        """Run a function in Matlab and return the result.

        Parameters
        ----------
        func_path: str
            Name of function to run or a path to an m-file.
        func_args: object, optional
            Function args to send to the function.
        nargout: int, optional
            Desired number of return arguments.
        kwargs:
            Keyword arguments are passed to Matlab in the form [key, val] so
            that matlab.plot(x, y, '--', LineWidth=2) would be translated into
            plot(x, y, '--', 'LineWidth', 2)

        Returns
        -------
        Result dictionary with keys: 'message', 'result', and 'success'
        """
        if not self.started:
            raise ValueError('Session not started, use start()')

        nargout = kwargs.pop('nargout', 1)
        func_args += tuple(item for pair in zip(kwargs.keys(), kwargs.values())
                           for item in pair)
        dname = os.path.dirname(func_path)
        fname = os.path.basename(func_path)
        func_name, ext = os.path.splitext(fname)
        if ext and not ext == '.m':
            raise TypeError('Need to give path to .m file')
        return self._json_response(cmd='eval',
                                   func_name=func_name,
                                   func_args=func_args or '',
                                   dname=dname,
                                   nargout=nargout)

    def run_code(self, code):
        """Run some code in Matlab command line provide by a string

        Parameters
        ----------
        code : str
            Code to send for evaluation.
        """
        return self.run_func('evalin', 'base', code, nargout=0)

    def _init_run_code(self):
        """Code to run at start of headless session to ensure sane
        environment."""
        code = "cd('%s')" % os.getcwd()
        return self.run_code(code)

    def get_variable(self, varname, default=None):
        resp = self.run_func('evalin', 'base', varname)
        return resp['result'] if resp['success'] else default

    def set_variable(self, varname, value):
        if isinstance(value, spmatrix):
            return self._set_sparse_variable(varname, value)
        return self.run_func('assignin', 'base', varname, value, nargout=0)

    def set_plot_settings(self, width=512, height=384, inline=True):
        if inline:
            code = ["set(0, 'defaultfigurevisible', 'off')"]
        else:
            code = ["set(0, 'defaultfigurevisible', 'on')"]
        size = "set(0, 'defaultfigurepaperposition', [0 0 %s %s])"
        code += ["set(0, 'defaultfigurepaperunits', 'inches')",
                 "set(0, 'defaultfigureunits', 'inches')",
                 size % (int(width) / 150., int(height) / 150.)]
        self.run_code(';'.join(code))

    def _set_sparse_variable(self, varname, value):
        value = value.todok()
        prefix = 'pymatbridge_temp_sparse_%s_' % uuid4().hex
        self.set_variable(prefix + 'keys', value.keys())
        # correct for 1-indexing in MATLAB
        self.run_code('{0}keys = {0}keys + 1;'.format(prefix))
        self.set_variable(prefix + 'values', value.values())
        cmd = "{1} = sparse({0}keys(:, 1), {0}keys(:, 2), {0}values');"
        result = self.run_code(cmd.format(prefix, varname))
        self.run_code('clear {0}keys {0}values'.format(prefix))
        return result

    def __getattr__(self, name):
        """If an attribute is not found, try to create a bound method"""
        return self._bind_method(name)

    def _bind_method(self, name, unconditionally=False):
        """Generate a Matlab function and bind it to the instance

        This is where the magic happens. When an unknown attribute of the
        Matlab class is requested, it is assumed to be a call to a
        Matlab function, and is generated and bound to the instance.

        This works because getattr() falls back to __getattr__ only if no
        attributes of the requested name can be found through normal
        routes (__getattribute__, __dict__, class tree).

        bind_method first checks whether the requested name is a callable
        Matlab function before generating a binding.

        Parameters
        ----------
        name : str
            The name of the Matlab function to call
                e.g. 'sqrt', 'sum', 'svd', etc
        unconditionally : bool, optional
            Bind the method without performing
                checks. Used to bootstrap methods that are required and
                know to exist

        Returns
        -------
        MatlabFunction
            A reference to a newly bound MatlabFunction instance if the
                requested name is determined to be a callable function

        Raises
        ------
        AttributeError: if the requested name is not a callable
                Matlab function

        """
        # TODO: This does not work if the function is a mex function inside a folder of the same name
        exists = self.run_func('exist', name)['result'] in [2, 3, 5]
        if not unconditionally and not exists:
            raise AttributeError("'Matlab' object has no attribute '%s'" % name)

        # create a new method instance
        method_instance = MatlabFunction(weakref.ref(self), name)
        method_instance.__name__ = name

        # bind to the Matlab instance with a weakref (to avoid circular references)
        if sys.version.startswith('3'):
            method = types.MethodType(method_instance, weakref.ref(self))
        else:
            method = types.MethodType(method_instance, weakref.ref(self),
                                      _Session)
        setattr(self, name, method)
        return getattr(self, name)


class Matlab(_Session):
    def __init__(self, executable='matlab', socket_addr=None,
                 id='python-matlab-bridge', log=False, maxtime=15,
                 platform=None, startup_options=None,
                 loglevel=logging.WARNING):
        """
        Initialize this thing.

        Parameters
        ----------

        executable : str
            A string that would start Matlab at the terminal. Per default, this
            is set to 'matlab'.

        socket_addr : str
            A string that represents a valid ZMQ socket address, such as
            "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:55555", etc. Default is
            to choose a random IPC file name, or a random socket (for TCP).

        id : str
            An identifier for this instance of the pymatbridge.

        log : str
            Location to log to, defaults to sys.stdout

        maxtime : float
           The maximal time to wait for a response from matlab (optional,
           Default is 15 sec)

        platform : string
           The OS of the machine on which this is running. Per default this
           will be taken from sys.platform.

        startup_options : string
           Command line options to pass to MATLAB. Optional; sensible defaults
           are used if this is not provided.
        """
        if platform is None:
            platform = sys.platform
        if startup_options is None:
            if platform == 'win32':
                startup_options = ' -automation -nosplash'
            else:
                startup_options = ' -nodesktop -nosplash'
        if log:
            startup_options += ' -logfile "{}"'.format(log)
        super(Matlab, self).__init__(executable, socket_addr, id, log, maxtime,
                                     platform, startup_options, loglevel)

    def _program_name(self):
        return 'MATLAB'

    def _execute_flag(self):
        return '-r'


class Octave(_Session):
    def __init__(self, executable='octave', socket_addr=None,
                 id='python-matlab-bridge', log=False, maxtime=15,
                 platform=None, startup_options=None,
                 loglevel=logging.WARNING):
        """
        Initialize this thing.

        Parameters
        ----------

        executable : str
            A string that would start Octave at the terminal. Per default, this
            is set to 'octave'.

        socket_addr : str
            A string that represents a valid ZMQ socket address, such as
            "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:55555", etc.

        id : str
            An identifier for this instance of the pymatbridge.

        log : bool
            Whether to save a log file in some known location.

        maxtime : float
           The maximal time to wait for a response from octave (optional,
           Default is 15 sec)

        platform : string
           The OS of the machine on which this is running. Per default this
           will be taken from sys.platform.

        startup_options : string
           Command line options to pass to Octave. Optional; sensible defaults
           are used if this is not provided.
        """
        if startup_options is None:
            startup_options = '--silent --no-gui'
        super(Octave, self).__init__(executable, socket_addr, id, log, maxtime,
                                     platform, startup_options)

    def _program_name(self):
        return 'Octave'

    def _init_run_code(self):
        code = super(Octave, self)._init_run_code()
        code.append("graphics_toolkit('gnuplot')")
        if self.log:
            code.append("diary('{}')".format(self.id))
        self.run_code(code)

    def _execute_flag(self):
        return '--eval'


class MatlabFunction(object):

    def __init__(self, parent, name):
        """An object representing a Matlab function

        Methods are dynamically bound to instances of Matlab objects and
        represent a callable function in the Matlab subprocess.

        Parameters
        ----------
        parent: Matlab instance
            A reference to the parent (Matlab instance) to which the
                MatlabFunction is being bound
        name: str
            The name of the Matlab function this represents
        """
        self.name = name
        self._parent = parent
        self.doc = None

    def __call__(self, unused_parent_weakref, *args, **kwargs):
        """Call a function with the supplied arguments in the Matlab subprocess

        Passes parameters to `run_func`.

        """
        return self.parent.run_func(self.name, *args, **kwargs)

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
            self.doc = self.parent.help(self.name)['result']
        return self.doc
