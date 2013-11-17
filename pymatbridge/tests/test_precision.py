import pymatbridge as pymat
import random as rd
import numpy as np
import numpy.testing as npt

def connectToMatlab():
    mlab = pymat.Matlab()
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "connectToMatlab(): Connection failed")

    return mlab


def stopMatlab(mlab):
    mlab.stop()
    npt.assert_(not mlab.is_connected(), msg = "stopMatlab(): Disconnection failed")


def testFloat64Roundtrip():
    mlab = connectToMatlab()

    for i in range(0,10):
        val = np.float64(rd.random())
        res = mlab.run_func('test_precision_pass.m',{'val':val})['result']
        npt.assert_almost_equal(res, val, decimal=4, err_msg="float64 roundtrip error")

    stopMatlab(mlab)


def testFloat64Sum():
    mlab = connectToMatlab()

    for i in range(0,10):
        val1 = np.float64(rd.random())
        val2 = np.float64(rd.random())

        res = mlab.run_func('test_precision_sum.m',{'val1':val1,'val2':val2})['result']
        npt.assert_almost_equal(res, val1 + val2, decimal=6, err_msg="float64 sum error")

    stopMatlab(mlab)


def test_tuple():
    pass


def test_dict():
    pass


def test_array():
    pass
