#!/usr/bin/env python
import os
import sys
import glob
import shutil
from setuptools import setup


# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def read(file_name):
  with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
    return f.read()

if sys.platform == "win32":
    raise ValueError("pymatbridge does not work on win32")
else:
    for copy_this in ["./messenger/mexmaci64/messenger.mexmaci64",
                      "./messenger/mexa64/messenger.mexa64",
                      "./messenger/mexw64/messenger.mexw64"]:
      shutil.copy(messenger, 'pymatbridge/matlab')
  
# ----------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------
__version__ = '0.4.dev'

setup(
    name = 'pymatbridge',
    version = __version__,
    platforms = 'OS Independent',
    description = 'A package to call Matlab functions from Python',
    long_description = read('README.md'),
    maintainer = 'Ariel Rokem',
    maintainer_email = 'arokem@gmail.com',
    url = 'https://github.com/arokem/python-matlab-bridge',
    download_url = 'https://github.com/arokem/python-matlab-bridge/archive/master.tar.gz',
    license = 'BSD',
    packages = [
        'pymatbridge'
    ],
    install_requires = [
        'numpy>=1.7.0',
        'pyzmq>=13.0.0'
    ],
    entry_points = {
        'console_scripts': [
            'publish-notebook = pymatbridge.publish:main'
        ]
    },
    package_data = {
        'pymatbridge': [
            'matlab/matlabserver.m',
            'matlab/messenger.*',
            'matlab/usrprog/*',
            'matlab/util/*.m',
            'matlab/util/json_v0.2.2/LICENSE',
            'matlab/util/json_v0.2.2/README.md',
            'matlab/util/json_v0.2.2/test/*',
            'matlab/util/json_v0.2.2/+json/*.m',
            'matlab/util/json_v0.2.2/+json/java/*',
            'tests/*.py',
            'examples/*.ipynb'
        ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ]
)
