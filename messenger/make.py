from __future__ import print_function

import os
import sys
import shlex
import shutil
import subprocess
import platform
import glob

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

from . import settings

__all__ = [
    'get_messenger_dir',
    'get_matlab_bin',
    'get_config',
    'do_build',
    'build_octave',
    'build_matlab'
]

def get_messenger_dir():
    host, is_64bit = platform.system(), platform.machine().endswith('64')
    ostype = {
        'Darwin':  'mexmaci64',
        'Linux':   'mexa64',
        'Windows': 'mexw64',
    }
    if not is_64bit and host == 'Windows':
        raise ValueError("pymatbridge does not support 32-bit Windows")

    return ostype[host] if is_64bit else 'mexw32'


def get_config(host, config='config.ini'):

    cfg = ConfigParser()
    cfg.read(config)

    return dict(cfg.items(host))


def do_build(make_cmd, messenger_exe):
    print('Building %s...' % messenger_exe)
    print(make_cmd)
    messenger_dir = get_messenger_dir()
    subprocess.call(shlex.split(make_cmd), stderr=subprocess.STDOUT)

    messenger_loc = os.path.join(messenger_dir, messenger_exe)

    shutil.move(messenger_exe, os.path.join('messenger', messenger_loc))

    if os.path.isfile('messenger.o'):
        os.remove('messenger.o')


def build_octave(static=False):
    paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s"
    paths = paths % get_config(platform.system())
    make_cmd = "mkoctfile --mex %s -lzmq ./src/messenger.c" % paths
    do_build(make_cmd, 'messenger.mex')


def build_matlab(static=False):
    """
    Build the messenger mex for MATLAB

    Parameters
    ----------
    static : bool
        Determines if the zmq library has been statically linked.
        If so, it will append the command line option -DZMQ_STATIC
        when compiling the mex so it matches libzmq.
    """
    matlab_bin, cfg = settings.get_matlab_bin(), get_config(platform.system())

    extcmd     = '%s' % os.path.join(matlab_bin, "mexext")
    extension  = subprocess.check_output(extcmd, shell=True)
    extension  = extension.decode('utf-8').rstrip()

    # Build the mex file
    mex = '"' + os.path.join(matlab_bin, "mex") + '"'
    paths    = "-L'%(zmq_lib)s' -I'%(zmq_inc)s'" % cfg
    make_cmd = '%s -O %s -lzmq messenger/src/messenger.c' % (mex, paths)

    if static:
        make_cmd += ' -DZMQ_STATIC'

    do_build(make_cmd, 'messenger.%s' % extension)


def get_matlab_bin(config='config.ini'):
    """
    Tries to find the MATLAB bin directory independent on host platform.
    The operation of this function can be overridden by setting the MATLAB_BIN
    variable within the configuration file specified.

    Parameters
    ----------
    config: str
        Relative path to configuration file

    Returns
    -------
    matlab: str
        Absolute path to matlab bin directory
    """
    host = platform.system()
    cfg  = get_config(host, config=config)
    programs = {
        'Darwin' : r'/Applications',
        'Windows': r'C:/Program Files',
        'Linux'  : r'/usr/local',
        }

    if cfg.get('MATLAB_BIN', None):
        matlab = cfg['MATLAB_BIN']
    else:
        # Searches for Matlab bin if it's not set
        _root    = [os.path.join(programs[host], p) for p in os.listdir(programs[host]) if p.startswith('MATLAB')][0]
        _version = [p for p in os.listdir(_root) if p.startswith('R20')]
        if _version:
            _root = r'%s/%s' % (_root, _version.pop())
        matlab   = r'%s/%s' % (_root, 'bin')

    assert os.path.isdir(matlab)

    return os.path.normpath(matlab)

