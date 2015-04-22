from __future__ import print_function

import os
import sys
import shlex
import shutil
import subprocess
import platform
import glob
import operator

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
    'build_matlab',
    'split_command_line',
]

def split_command_line(command_line):
    """
    This splits a command line into a list of arguments. It splits arguments
    on spaces, but handles embedded quotes, double quotes, and escaped
    characters. It's impossible to do this with a regular expression, so I
    wrote a little state machine to parse the command line.
    """
    arg_list = []
    arg = ''

    # Constants to name the states we can be in.
    state_basic = 0
    state_esc = 1
    state_singlequote = 2
    state_doublequote = 3
    # The state when consuming whitespace between commands.
    state_whitespace = 4
    state = state_basic

    for c in command_line:
        if state == state_basic or state == state_whitespace:
            if c == '\\':
                # Escape the next character
                state = state_esc
            elif c == r"'":
                # Handle single quote
                state = state_singlequote
            elif c == r'"':
                # Handle double quote
                state = state_doublequote
            elif c.isspace():
                # Add arg to arg_list if we aren't in the middle of whitespace.
                if state == state_whitespace:
                    # Do nothing.
                    None
                else:
                    arg_list.append(arg)
                    arg = ''
                    state = state_whitespace
            else:
                arg = arg + c
                state = state_basic
        elif state == state_esc:
            arg = arg + c
            state = state_basic
        elif state == state_singlequote:
            if c == r"'":
                state = state_basic
            else:
                arg = arg + c
        elif state == state_doublequote:
            if c == r'"':
                state = state_basic
            else:
                arg = arg + c

    if arg != '':
        arg_list.append(arg)
    return arg_list

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

    messenger_dir = get_messenger_dir()
    use_shell     = sys.platform.startswith('win32')

    print('Building %s...' % messenger_exe)
    print(make_cmd)

    subprocess.check_output(make_cmd, shell=use_shell)

    messenger_loc = os.path.join(messenger_dir, messenger_exe)

    shutil.move(messenger_exe, os.path.join('messenger', messenger_loc))

    if os.path.isfile('messenger.o'):
        os.remove('messenger.o')


def build_octave(static=False):

    paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s"
    paths = paths % get_config(platform.system())
    make_cmd = "mkoctfile --mex %s -lzmq messenger/src/messenger.c" % paths

    do_build(split_command_line(make_cmd), 'messenger.mex')


def build_matlab(static=False, messenger='messenger.c'):
    """
    Build the messenger mex for MATLAB

    Parameters
    ----------
    static : bool
        Determines if the zmq library has been statically linked.
        If so, it will append the command line option -DZMQ_STATIC
        when compiling the mex so it matches libzmq.
    """
    matlab_bin, cfg = get_matlab_bin(), get_config(platform.system())

    use_shell  = sys.platform.startswith('win32')
    extcmd     = split_command_line(os.path.join(matlab_bin, "mexext"))
    extension  = subprocess.check_output(extcmd, shell=use_shell)
    extension  = extension.decode('utf-8').rstrip()

    # Build the mex file
    mex = os.path.join(matlab_bin, "mex")
    paths    = "-L'%(zmq_lib)s' -I'%(zmq_inc)s'" % cfg
    make_cmd = '%s -O %s -lzmq %s' % (mex, paths, messenger)

    if static:
        make_cmd += ' -DZMQ_STATIC'

    print(make_cmd)
    subprocess.check_output(split_command_line(make_cmd), shell=use_shell)


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
    matlab: str or None
        Absolute path to matlab bin directory.
        Returns None if Matlab path could not be determined
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
        matlab   = [p for p in os.listdir(programs[host]) if p.startswith('MATLAB')]

        if not matlab:
            return None

        for p in os.listdir(os.path.join(programs[host], *matlab)):
            if p.startswith('R20'):
                matlab.append(p)

        matlab.append('bin')

    return os.path.normpath(os.path.join(programs[host], *matlab))
