#!/usr/bin/python

import os
import sys
import fnmatch
import subprocess

def find_path(candidates, target):
    for candidate in candidates:
        candidate = os.path.expanduser(candidate.rstrip('\r\n'))
	if os.path.exists(candidate):
            for root, dirnames, filenames in os.walk(candidate):
                for filename in fnmatch.filter(filenames, target):
                    return os.path.join(root)


    return ""

# Get the configuration file path
if (len(sys.argv) == 2):
    config_file = sys.argv[1]
else:
    print "Failed to build messenger. No configuration file provided."
    raise SystemExit

# Open the configuration file and start parsing
config = open(config_file, 'r')

# Check the system platform first
platform = sys.platform
print "This is a " + platform + " system"

for line in config:
    path = line.split('=')

    if path[0] == "MATLAB_BIN":
        matlab_path = path[1].rstrip('\r\n')
        if matlab_path == "":
            raise ValueError("Could not find Matlab bin directory. Please add it to MATLAB_BIN")
        print "Matlab found in " + matlab_path

    elif path[0] == "HEADER_PATH":
        print "Searching for zmq.h ..."
        header_path = find_path(path[1].split(','), 'zmq.h')

        if header_path == "":
            raise ValueError("Could not find zmq.h. Please add its path to local.cfg")

        print "zmq.h found in " + header_path

    elif path[0] == "LIB_PATH":
        # Dynamic library has different names on different platforms
        if platform == 'darwin':
            print "Searching for libzmq.dylib ..."
            lib_path = find_path(path[1].split(','), 'libzmq.dylib')
        elif platform == 'linux2':
            print "Searching for libzmq.so ..."
            lib_path = find_path(path[1].split(','), 'libzmq.so')
        elif platform == 'win32':
            print "Searching for libzmq.dll ..."
            lib_path = find_path(path[1].split(','), 'libzmq.dll')

        if lib_path == "":
            raise ValueError("Could not find zmq library. Please add its path to local.cfg")

	print "zmq library found in " + lib_path

config.close()

# Get the extension
if platform == 'win32':
    extcmd = '"' + matlab_path + "\\mexext.bat" + '"'
    check_extension = subprocess.Popen(extcmd, stdout = subprocess.PIPE)
    extension = check_extension.stdout.readline().rstrip('\r\n')
else:
    extcmd = matlab_path + "/mexext"
    check_extension = subprocess.Popen(extcmd, stdout = subprocess.PIPE)
    extension = check_extension.stdout.readline().rstrip('\r\n')

print "Building messenger." + extension + " ..."

# Build the mex file
if platform == 'win32':
    mex = "\\mex.bat"
else:
    mex = "/mex"
make_cmd = '"' + matlab_path + mex + '"' + " -O -I" + header_path + " -L" + lib_path + " -lzmq pymatbridge/src/messenger.c"
os.system(make_cmd)

print "Moving messenger." + extension + " to pymatbridge/matlab/ ..."

# Move to the ../matlab/ directory
if platform == 'win32':
    move_cmd = "move messenger." + extension + " pymatbridge\\matlab\\"
else:
    move_cmd = "mv messenger." + extension + " pymatbridge/matlab/"

os.system(move_cmd)

