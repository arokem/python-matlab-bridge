#!/usr/bin/python
from __future__ import print_function
import os
import platform
import sys
import shlex
import shutil
import subprocess

use_shell = True if sys.platform.startswith("win32") else False


def make_str(byte_or_str):
    return byte_or_str if isinstance(byte_or_str, str) \
        else str(byte_or_str.decode("UTF-8"))


def esc(path):
    if ' ' in path:
        return '"' + path + '"'
    else:
        return path


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
    subprocess.check_output(shlex.split(make_cmd), shell=use_shell)

    messenger_loc = os.path.join(messenger_dir, messenger_exe)

    shutil.move(messenger_exe, messenger_loc)

    if os.path.exists('messenger.o'):
        os.remove('messenger.o')


def build_octave():
    paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s"
    paths = paths % get_config()
    make_cmd = "mkoctfile --mex %s -lzmq ./src/messenger.c" % paths
    do_build(make_cmd, 'messenger.mex')


def which_matlab():
    try:
        matlab_path = subprocess.check_output(['which', 'matlab']).strip()
        matlab_path = make_str(matlab_path)
        return os.path.dirname(os.path.realpath(matlab_path))
    except (OSError, subprocess.CalledProcessError):
        def ensure_path(path, extension=''):
            return os.path.isdir(path) and \
                os.path.isfile(os.path.join(path, "matlab" + extension))

        # need to guess the location of MATLAB
        if sys.platform.startswith("darwin"):
            MATLABs = [os.path.join("/Applications", i, "bin")
                       for i in os.listdir("/Applications")
                       if i.startswith("MATLAB_R")]
            # only want ones with MATLAB executables
            # sort so we can get the latest
            MATLABs = list(sorted(filter(ensure_path, MATLABs)))
            return MATLABs[-1] if len(MATLABs) > 0 else None
        elif sys.platform.startswith("win32"):
            MATLAB_loc = "C:\\Program Files\\MATLAB"
            print(MATLAB_loc)
            if not os.path.isdir(MATLAB_loc):
                return None
            MATLABs = [os.path.join(MATLAB_loc, i, "bin")
                       for i in os.listdir(MATLAB_loc)]
            print(MATLABs)
            print(i)
            # only want ones with MATLAB executables
            # sort so we can get the latest
            MATLABs = list(sorted(filter(lambda x: ensure_path(x, ".exe"),
                                         MATLABs)))
            print(MATLABs)
            return MATLABs[-1] if len(MATLABs) > 0 else None
        elif sys.platform.startswith("linux"):
            MATLAB_loc = "/usr/local/MATLAB/"
            if not os.path.isdir(MATLAB_loc):
                return None
            MATLABs = [os.path.join(MATLAB_loc, i, "bin")
                       for i in os.listdir(MATLAB_loc)
                       if i.startswith("R")]
            # only want ones with MATLAB executables
            # sort so we can get the latest
            MATLABs = list(sorted(filter(ensure_path, MATLABs)))
            return MATLABs[-1] if len(MATLABs) > 0 else None


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
    if 'matlab_bin' in cfg and cfg['matlab_bin'] != '.':
        matlab_bin = cfg['matlab_bin'].strip('"')
    else:  # attempt to autodetect MATLAB filepath
        matlab_bin = which_matlab()
        if matlab_bin is None:
            raise ValueError("specify 'matlab_bin' in cfg file")
    # Get the extension
    extcmd = esc(os.path.join(matlab_bin, "mexext"))
    extension = subprocess.check_output(extcmd, shell=use_shell)
    extension = extension.decode('utf-8').rstrip('\r\n')

    # Build the mex file
    mex = esc(os.path.join(matlab_bin, "mex"))
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
        if args.static:
            raise ValueError("static building not yet supported for octave")
        build_octave()
    else:
        raise ValueError()
