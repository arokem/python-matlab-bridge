import pymatbridge as pymat
import IPython

import random as rd
import numpy as np
import numpy.testing as npt

class TestMagic:

    # Create an IPython shell and load Matlab magic
    @classmethod
    def setup_class(cls):
        cls.ip = IPython.InteractiveShell()
        pymat.load_ipython_extension(cls.ip)

    # Unload the magic, shut down Matlab
    @classmethod
    def teardown_class(cls):
        pymat.unload_ipython_extension(cls.ip)

