#!/usr/bin/python
from __future__ import print_function
import os
import platform
import sys
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
    subprocess.check_output(make_cmd.split())

    messenger_loc = os.path.join(messenger_dir, messenger_exe)

    shutil.move(messenger_exe, messenger_loc)
    os.remove('messenger.o')


def build_octave():
    paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s"
    paths = paths % get_config()
    make_cmd = "mkoctfile --mex %s -lzmq ./src/messenger.c" % paths
    do_build(make_cmd, 'messenger.mex')


def build_matlab():
    cfg = get_config()
    matlab_bin = cfg['matlab_bin']
    # Get the extension
    if sys.platform == 'win32':
        extcmd = '"%s\\mexext.bat"' % matlab_bin
    else:
        extcmd = matlab_bin + "/mexext"

    check_extension = subprocess.Popen(extcmd, stdout=subprocess.PIPE)
    extension = check_extension.stdout.read()
    extension = extension.decode('utf-8').rstrip('\r\n')

    # Build the mex file
    if sys.platform == 'win32':
        mex = matlab_bin + "\\mex.bat"
    else:
        mex = matlab_bin + "/mex"
    paths = "-L%(zmq_lib)s -I%(zmq_inc)s" % cfg
    make_cmd = '"%s" -O %s -lzmq ./src/messenger.c' % (mex, paths)
    do_build(make_cmd, 'messenger.%s' % extension)


if __name__ == '__main__':
    usage = 'Please specify a valid make target (Matlab or Octave)'
    if len(sys.argv) < 1:
        print(usage)
        sys.exit()
    if sys.argv[1].lower() == 'matlab':
        build_matlab()
    elif sys.argv[1].lower() == 'octave':
        build_octave()
    else:
        print(usage)
