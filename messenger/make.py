from __future__ import print_function

import os
import sys
import shlex
import shutil
import subprocess
import platform

from glob import glob

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

from . import settings

__all__ = [
    'get_messenger_dir',
    'get_config',
    'do_build',
    'build_octave',
    'build_matlab'
]

def get_messenger_dir():
    host, is_64bit = platform.system(), sys.maxsize > 2**32
    ostype = {
        'Darwin':  'mexmaci64',
        'Linux':   'mexa64',
        'Windows': 'mexw64',
    }
    if not is_64bit and host == 'Windows':
        raise ValueError("pymatbridge does not support 32-bit Windows")

    return ostype[host] if is_64bit else 'mexw32'


def get_config():
    config = os.path.join(os.path.realpath(__file__), 'config.ini')
    print(config)
    cfg = ConfigParser()
    config.read(config)
    return cfg


def do_build(make_cmd, messenger_exe):
    print('Building %s...' % messenger_exe)
    print(make_cmd)
    messenger_dir = 'messenger' + '/' + get_messenger_dir()
    subprocess.call(shlex.split(make_cmd), stderr=subprocess.STDOUT)

    messenger_loc = os.path.join(messenger_dir, messenger_exe)

    # shutil.move(messenger_exe, messenger_loc)

    if os.path.isfile('messenger.o'):
        os.remove('messenger.o')


def build_octave():
    paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s"
    paths = paths % get_config()
    make_cmd = "mkoctfile --mex %s -lzmq ./src/messenger.c" % paths
    do_build(make_cmd, 'messenger.mex')


def build_matlab(static=False):
    """
    Build the messenger mex for MATLAB

    Parameters
    ============
    static : bool
        Determines if the zmq library has been statically linked.
        If so, it will append the command line option -DZMQ_STATIC
        when compiling the mex so it matches libzmq.
    """
    matlab_bin = settings.get_matlab_bin()
    cfg, host = ConfigParser(), platform.system()
    cfg.read('config.ini')
    libzmq = {
        'zmq_lib': os.path.normpath(cfg.get(host, 'ZMQ_LIB')),
        'zmq_inc': os.path.normpath(cfg.get(host, 'ZMQ_INC')),
    }

    extcmd     = '%s' % os.path.join(matlab_bin, "mexext")
    extension  = subprocess.check_output(extcmd, shell=True)
    extension  = os.path.join('messenger', extension.decode('utf-8').rstrip())

    # Build the mex file
    mex = '"' + os.path.join(matlab_bin, "mex") + '"'
    paths    = "-L'%(zmq_lib)s' -I'%(zmq_inc)s'" % libzmq
    make_cmd = '%s -O %s -lzmq messenger/src/messenger.c' % (mex, paths)

    if static:
        make_cmd += ' -DZMQ_STATIC'

    do_build(make_cmd, 'messenger.%s' % extension)
