#!/usr/bin/python
from __future__ import print_function
import os
import platform
import sys
import shlex
import shutil
import subprocess


def get_messenger_dir():
    # Check the system platform first
    splatform = sys.platform

    if splatform.startswith('linux'):
        messenger_dir = 'mexa64'
    elif splatform.startswith('darwin'):
        messenger_dir = 'mexmaci64'
    elif splatform.startswith('win32'):
        if splatform == "win32":
            # We have a win64 messenger, so we need to figure out if this is 32
            # or 64 bit Windows:
            if not platform.machine().endswith('64'):
                raise ValueError("pymatbridge does not work on win32")

        # We further need to differniate 32 from 64 bit:
        maxint = sys.maxsize
        if maxint == 9223372036854775807:
            messenger_dir = 'mexw64'
        elif maxint == 2147483647:
            messenger_dir = 'mexw32'
    return messenger_dir


def get_config():
    messenger_dir = get_messenger_dir()
    with open(os.path.join(messenger_dir, 'local.cfg')) as fid:
        lines = fid.readlines()

    cfg = {}
    for line in lines:
        if '=' not in line:
            continue
        name, path = line.split('=')
        cfg[name.lower()] = path.strip() or '.'
    return cfg


def do_build(make_cmd, messenger_exe):
    print('Building %s...' % messenger_exe)
    print(make_cmd)
    messenger_dir = get_messenger_dir()
    subprocess.check_output(shlex.split(make_cmd), shell=True)

    messenger_loc = os.path.join(messenger_dir, messenger_exe)

    shutil.move(messenger_exe, messenger_loc)

    if os.path.exists('messenger.o'):
        os.remove('messenger.o')


def build_octave():
    paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s"
    paths = paths % get_config()
    make_cmd = "mkoctfile --mex %s -lzmq ./src/messenger.c" % paths
    do_build(make_cmd, 'messenger.mex')


def build_matlab(static=False):
    """build the messenger mex for MATLAB
    
    static : bool
        Determines if the zmq library has been statically linked.
        If so, it will append the command line option -DZMQ_STATIC
        when compiling the mex so it matches libzmq.
    """
    cfg = get_config()
    # To deal with spaces, remove quotes now, and add
    # to the full commands themselves.
    matlab_bin = cfg['matlab_bin'].strip('"')
    # Get the extension
    extcmd = '"' + os.path.join(matlab_bin, "mexext") + '"'
    extension = subprocess.check_output(extcmd, shell=True)
    extension = extension.decode('utf-8').rstrip('\r\n')

    # Build the mex file
    mex = '"' + os.path.join(matlab_bin, "mex") + '"'
    paths = "-L%(zmq_lib)s -I%(zmq_inc)s" % cfg
    make_cmd = '%s -O %s -lzmq ./src/messenger.c' % (mex, paths)
    if static:
        make_cmd += ' -DZMQ_STATIC'
    do_build(make_cmd, 'messenger.%s' % extension)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        choices=["matlab", "octave"],
        type=str.lower,
        help="target to be built")
    parser.add_argument("--static", action="store_true",
                        help="staticly link libzmq")
    args = parser.parse_args()
    if args.target == "matlab":
        build_matlab(static=args.static)
    elif args.target == "octave":
        build_octave()
    else:
        raise ValueError()
