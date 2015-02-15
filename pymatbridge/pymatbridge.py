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
{'content': {'stdout': '', 'datadir': '/private/tmp/MatlabData/', 'code': 'a=1;', 'figures': []}, 'success': 'true'}
>>> m.get_variable('a')
1

"""

import os
import time
import codecs
import zmq
import subprocess
import sys
import json
from uuid import uuid4

try:
    from numpy import ndarray, generic, float64, frombuffer, asfortranarray
except ImportError:
    class ndarray:
        pass
    generic = ndarray

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
        obj = asfortranarray(obj)
    else:
        obj = obj.T
    try:
        data = obj.astype(float64).tobytes()
    except AttributeError:
        data = obj.astype(float64).tostring()

    data = codecs.encode(data, 'base64').decode('utf-8')
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
    return frombuffer(codecs.decode(data, 'base64'), float64)


# JSON decoder for arrays and complex numbers
def decode_pymat(dct):
    if 'ndarray' in dct and 'data' in dct:
        value = decode_arr(dct['data'])
        shape = decode_arr(dct['shape'])
        return value.reshape(shape, order='F')
    elif 'ndarray' in dct and 'imag' in dct:
        real = decode_arr(dct['real'])
        imag = decode_arr(dct['imag'])
        shape = decode_arr(dct['shape'])
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

    def __init__(self, executable, socket_addr=None,
                 id='python-matlab-bridge', log=False, maxtime=60,
                 platform=None, startup_options=None):
        """
        Initialize this thing.

        Parameters
        ----------

        executable : str
            A string that would start the session at the terminal.

        socket_addr : str
            A string that represents a valid ZMQ socket address, such as
            "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:55555", etc.

        id : str
            An identifier for this instance of the pymatbridge.

        log : bool
            Whether to save a log file in some known location.

        maxtime : float
           The maximal time to wait for a response from the session (optional,
           Default is 10 sec)

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

        if socket_addr is None:
            self.socket_addr = "tcp://127.0.0.1:55555" if self.platform == "win32" else "ipc:///tmp/pymatbridge"

        if self.log:
            startup_options += ' > ./pymatbridge/logs/bashlog_%s.txt' % self.id

        self.context = None
        self.socket = None

    def _program_name(self):
        raise NotImplemented

    def _preamble_code(self):
        # suppress warnings while loading the path, in the case of
        # overshadowing a built-in function on a newer version of
        # Matlab (e.g. isrow)
        return ["old_warning_state = warning('off','all')",
                "addpath(genpath('%s'))" % MATLAB_FOLDER,
                "warning(old_warning_state)",
                "clear old_warning_state"]

    def _execute_flag(self):
        raise NotImplemented

    def _run_server(self):
        code = self._preamble_code()
        code.extend([
            "matlabserver('%s')" % self.socket_addr,
            'exit'
        ])
        command = '%s %s %s "%s"' % (self.executable, self.startup_options,
                                     self._execute_flag(), ','.join(code))
        subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)

    # Start server/client session and make the connection
    def start(self):
        # Start the MATLAB server in a new process
        print("Starting %s on ZMQ socket %s" % (self._program_name(), self.socket_addr))
        print("Send 'exit' command to kill the server")
        self._run_server()

        # Start the client
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.socket_addr)

        self.started = True

        # Test if connection is established
        if self.is_connected():
            print("%s started and connected!" % self._program_name())
            self.set_default_plot_size()
            return True
        else:
            print("%s failed to start" % self._program_name())
            return False

    def _response(self, **kwargs):
        req = json.dumps(kwargs, cls=PymatEncoder)
        self.socket.send_string(req)
        resp = self.socket.recv_string()
        return resp

    # Stop the Matlab server
    def stop(self):
        # Matlab should respond with "exit" if successful
        if self._response(cmd='exit') == "exit":
            print("%s closed" % self._program_name())

        self.started = False
        return True

    # To test if the client can talk to the server
    def is_connected(self):
        if not self.started:
            time.sleep(2)
            return False

        req = json.dumps(dict(cmd="connect"), cls=PymatEncoder)
        self.socket.send_string(req)

        start_time = time.time()
        while True:
            try:
                resp = self.socket.recv_string(flags=zmq.NOBLOCK)
                return resp == "connected"
            except zmq.ZMQError:
                sys.stdout.write('.')
                time.sleep(1)
                if time.time() - start_time > self.maxtime:
                    print("%s session timed out after %d seconds" % (self._program_name(), self.maxtime))
                    return False

    def is_function_processor_working(self):
        result = self.run_func('%s/usrprog/test_sum.m' % MATLAB_FOLDER,
                {'echo': '%s: Function processor is working!' % self._program_name()})
        return result['success'] == 'true'

    def _json_response(self, **kwargs):
        return json.loads(self._response(**kwargs), object_hook=decode_pymat)

    def run_func(self, func_path, func_args=None, nargout=1):
        """Run a function in Matlab and return the result.

        Parameters
        ----------
        func_path: str
            Name of function to run or a path to an m-file.
        func_args: object
            Function args to send to the function.
        nargout: int
            Desired number of return arguments.

        Returns
        -------
        Result dictionary with keys: 'message', 'result', and 'success'
        """
        return self._json_response(cmd='run_function',
                                   func_path=func_path,
                                   func_args=func_args,
                                   nargout=nargout)

    def run_code(self, code):
        """Run some code in Matlab command line provide by a string

        Parameters
        ----------
        code : str
            Code to send for evaluation.
        """
        return self._json_response(cmd='run_code', code=code)

    def get_variable(self, varname, default=None):
        response = self._json_response(cmd='get_var', varname=varname)
        return response['var'] if response['exists'] else default

    def set_variable(self, varname, value):
        if isinstance(value, spmatrix):
            return self._set_sparse_variable(varname, value)
        return self.run_func('pymat_set_variable.m',
                             {'name': varname, 'value': value})

    def set_default_plot_size(self, width=512, height=384):
        code = "set(0, 'defaultfigurepaperunits', 'inches');\n"
        code += "set(0, 'defaultfigureunits', 'inches');\n"
        size = "set(0, 'defaultfigurepaperposition', [0 0 %s %s])\n;"
        code += size % (int(width) / 150., int(height) / 150.)
        self.run_code(code)

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


class Matlab(_Session):
    def __init__(self, executable='matlab', socket_addr=None,
                 id='python-matlab-bridge', log=False, maxtime=60,
                 platform=None, startup_options=None):
        """
        Initialize this thing.

        Parameters
        ----------

        executable : str
            A string that would start Matlab at the terminal. Per default, this
            is set to 'matlab', so that you can alias in your bash setup

        socket_addr : str
            A string that represents a valid ZMQ socket address, such as
            "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:55555", etc.

        id : str
            An identifier for this instance of the pymatbridge.

        log : bool
            Whether to save a log file in some known location.

        maxtime : float
           The maximal time to wait for a response from matlab (optional,
           Default is 10 sec)

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
                startup_options = ' -automation -noFigureWindows'
            else:
                startup_options = ' -nodesktop -nodisplay'
        if log:
            startup_options += ' -logfile ./pymatbridge/logs/matlablog_%s.txt' % id
        super(Matlab, self).__init__(executable, socket_addr, id, log, maxtime,
                                     platform, startup_options)

    def _program_name(self):
        return 'MATLAB'

    def _execute_flag(self):
        return '-r'


class Octave(_Session):
    def __init__(self, executable='octave', socket_addr=None,
                 id='python-matlab-bridge', log=False, maxtime=60,
                 platform=None, startup_options=None):
        """
        Initialize this thing.

        Parameters
        ----------

        executable : str
            A string that would start Octave at the terminal. Per default, this
            is set to 'octave', so that you can alias in your bash setup

        socket_addr : str
            A string that represents a valid ZMQ socket address, such as
            "ipc:///tmp/pymatbridge", "tcp://127.0.0.1:55555", etc.

        id : str
            An identifier for this instance of the pymatbridge.

        log : bool
            Whether to save a log file in some known location.

        maxtime : float
           The maximal time to wait for a response from octave (optional,
           Default is 10 sec)

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

    def _preamble_code(self):
        code = super(Octave, self)._preamble_code()
        if self.log:
            code.append("diary('./pymatbridge/logs/octavelog_%s.txt')" % self.id)
        code.append("set(0, 'defaultfigurevisible', 'off');")
        code.append("graphics_toolkit('gnuplot')")
        return code

    def _execute_flag(self):
        return '--eval'
