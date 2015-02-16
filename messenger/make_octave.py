#!/usr/bin/python
from __future__ import print_function
import os
from get_messenger_dir import get_messenger_dir
import shutil
import subprocess

messenger_dir = get_messenger_dir()

with open(os.path.join(messenger_dir, 'local_octave.cfg')) as fid:
    lines = fid.readlines()

cfg = {}
for line in lines:
    name, path = line.split('=')
    cfg[name.lower()] = path.strip() or '.'

print("Building messenger.mex...")

paths = "-L%(octave_lib)s -I%(octave_inc)s -L%(zmq_lib)s -I%(zmq_inc)s" % cfg
make_cmd = "mkoctfile --mex %s -lzmq ./src/messenger.c" % paths
print(make_cmd)
subprocess.check_output(make_cmd.split())

messenger_exe = 'messenger.mex'
messenger_loc = os.path.join(messenger_dir, messenger_exe)

shutil.move(messenger_exe, messenger_loc)
os.remove('messenger.o')
