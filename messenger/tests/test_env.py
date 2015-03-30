import numpy.testing as npt
import sys
import os

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

# Necessary since messenger is not installed with pymatbridge
sys.path.append(ROOT)

import messenger

def test_matlab_bin():
    config = os.path.join(ROOT, 'config.ini')
    npt.assert_equal(os.path.isfile(config), True)
    bin = messenger.get_matlab_bin(config=config)
    npt.assert_equal(os.path.isdir(bin), True)

    mexext = any(m for m in os.listdir(bin) if m == 'mexext' or m == 'mexext.exe')
    mex    = any(m for m in os.listdir(bin) if m == 'mex' or m == 'mex.exe')

    npt.assert_equal(mexext, True)
    npt.assert_equal(mex, True)

def test_matlab_env():
    config = os.path.join(ROOT, 'config.ini')
    matlab    = os.path.join(messenger.get_matlab_bin(config=config), 'matlab')
    env       = messenger.get_matlab_env(matlab=matlab)
    arch = env['ARCH']

    npt.assert_equal(arch.endswith(messenger.get_messenger_dir()[-2:]), True)

