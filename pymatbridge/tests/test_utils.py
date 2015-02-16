import os
import pymatbridge as pymat
import numpy.testing as npt

def on_octave():
    return bool(os.environ.get('USE_OCTAVE', False))

def connect_to_matlab():
    mlab = pymat.Octave() if on_octave() else pymat.Matlab(log=True)
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "connect_to_matlab(): Connection failed")

    return mlab


def stop_matlab(mlab):
    mlab.stop()
    npt.assert_(not mlab.is_connected(), msg = "stop_matlab(): Disconnection failed")


    
    
