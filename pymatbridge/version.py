"""pymatbridge version/release information"""

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 6
_version_micro = 0 #''  # use '' for first of series, number for 1 and above
_version_extra = 'dev'
#_version_extra = ''  # Uncomment this for full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: BSD License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

description = "pymatbridge is a set of python and matlab functions to allow these two systems to talk to each other"

long_description = """

Pymatbridge
===========

A python interface to call out to Matlab(R).


License information
===================

Copyright (c) 2012 -- , Max Jaderberg, Ariel Rokem, Haoxing Zhao
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

Neither the name of the Oxford University, Stanford University nor the names of
its contributors may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 'AS IS' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

NAME = "pymatbridge"
MAINTAINER = "Ariel Rokem"
MAINTAINER_EMAIL = "arokem@gmail.com"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "https://github.com/arokem/python-matlab-bridge"
DOWNLOAD_URL = "https://github.com/arokem/python-matlab-bridge/archive/master.tar.gz"
LICENSE = "BSD"
AUTHOR = "https://github.com/arokem/python-matlab-bridge/contributors"
AUTHOR_EMAIL = "arokem@gmail.com"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGES = ['pymatbridge',
            'pymatbridge.messenger']
PACKAGE_DATA = {"pymatbridge": ["matlab/matlabserver.m", "matlab/messenger.*",
                                "matlab/usrprog/*", "matlab/util/*.m",
                                "matlab/util/json_v0.2.2/LICENSE",
                                "matlab/util/json_v0.2.2/README.md",
                                "matlab/util/json_v0.2.2/test/*",
                                "matlab/util/json_v0.2.2/json/*.m",
                                "matlab/util/json_v0.2.2/json/java/*",
                                "tests/*.py", "tests/*.m", "examples/*.ipynb"],
                 "pymatbridge.messenger": ["mexmaci64/*",
                                           "mexw64/*",
                                           "mexa64/*"]}

REQUIRES = ['pyzmq']
EXTRAS_REQUIRE = {
    'sparse arrays':  ["scipy>=0.13.0"],
    'ipython': ["ipython>=3.0"],
}

BIN=['scripts/publish-notebook']
