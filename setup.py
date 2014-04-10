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


# ----------------------------------------------------------------------------
# MEX MESSENGER
# ----------------------------------------------------------------------------
messengers = {
    'darwin': ['messenger/mexmaci64/messenger.mexmaci64'],
    'linux2': ['messenger/mexa64/messenger.mexa64'],
    'win32':  ['messenger/mexw64/messenger.mexw64',
               'messenger/mexw32/messenger.mexw32']
}.get(sys.platform, [])

for messenger in messengers:
    try:
        shutil.copy(messenger, 'pymatbridge/matlab')
    except IOError:
        pass

if not glob.glob('pymatbridge/matlab/messenger.mex*'):
    raise IOError('The Matlab messenger mex script is not yet built for your system. '
                  'Please build messenger/src/messenger.c manually and copy the '
                  'binary to pymatbridge/matlab before continuing with setup.')


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
