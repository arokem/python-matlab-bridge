import pymatbridge as pymat
import numpy.testing as npt

def connect_to_matlab():
    mlab = pymat.Matlab()
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "connect_to_matlab(): Connection failed")

    return mlab


def stop_matlab(mlab):
    mlab.stop()
    npt.assert_(not mlab.is_connected(), msg = "stop_matlab(): Disconnection failed")

