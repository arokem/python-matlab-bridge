#!/usr/bin/python
from __future__ import print_function
import os
import sys
import shutil
import subprocess

# Check the system platform first
platform = sys.platform
print("This is a " + platform + " system")

if platform.startswith('linux'):
    messenger_dir = 'mexa64'
elif platform.startswith('darwin'):
    messenger_dir = 'mexmaci64'
elif platform.startswith('win32'):
    # We further need to differniate 32 from 64 bit:
    maxint = sys.maxsize
    if maxint == 9223372036854775807:
        messenger_dir = 'mexw64'
    elif maxint == 2147483647:
        messenger_dir = 'mexw32'

with open(os.path.join(messenger_dir, 'local_octave.cfg')) as fid:
    lines = fid.readlines()

cfg = {}
for line in lines:
    name, path = line.split('=')
    cfg[name.lower()] = path

print("Building messenger.oct...")

paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s" % cfg
make_cmd = "mkoctfile %s -lzmq ./src/messenger.c" % paths
print(make_cmd)
subprocess.check_output(make_cmd.split())

messenger_exe = 'messenger.oct'
messenger_loc = os.path.join(messenger_dir, messenger_exe)

shutil.move(messenger_exe, messenger_loc)
os.remove('messenger.o')
