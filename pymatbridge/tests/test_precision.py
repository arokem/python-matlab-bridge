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


# Pass a 64-bit floating number through the signal path
def testFloat64Roundtrip():
    mlab = connectToMatlab()

    for i in range(0,10):
        val = np.float64(rd.random())
        res = mlab.run_func('test_precision_pass.m',{'val':val})['result']
        npt.assert_almost_equal(res, val, decimal=8, err_msg="Float64 roundtrip error")

    stopMatlab(mlab)


# Add two 64-bit floating number in Matlab and return the sum
def testFloat64Sum():
    mlab = connectToMatlab()

    for i in range(0,10):
        val1 = np.float64(rd.random())
        val2 = np.float64(rd.random())

        res = mlab.run_func('test_precision_sum.m',{'val1':val1,'val2':val2})['result']
        npt.assert_almost_equal(res, val1 + val2, decimal=8, err_msg="Float64 sum error")

    stopMatlab(mlab)


# Multiply two 64-bit floating number in Matlab and return the product
def testFloat64Multiply():
    mlab = connectToMatlab()

    for i in range(0,10):
        val1 = np.float64(rd.random())
        val2 = np.float64(rd.random())

        res = mlab.run_func('test_precision_multiply.m',{'val1':val1,'val2':val2})['result']
        npt.assert_almost_equal(res, val1 * val2, decimal=8, err_msg="Float64 multiply error")

    stopMatlab(mlab)


# Make a division in Matlab and return the results
def testFloat64Divide():
    mlab = connectToMatlab()

    for i in range(0,10):
        val1 = np.float64(rd.random())
        val2 = np.float64(rd.random())

        res = mlab.run_func('test_precision_divide.m',{'val1':val1,'val2':val2})['result']
        npt.assert_almost_equal(res, val1 / val2, decimal=8, err_msg="Float64 divide error")

    stopMatlab(mlab)


# Calculate the square root in Matlab and return the result
def testFloat64Sqrt():
    mlab = connectToMatlab()

    for i in range(0,10):
        val = np.float64(rd.random())

        res = mlab.run_func('test_precision_sqrt.m',{'val':val})['result']
        npt.assert_almost_equal(res, np.sqrt(val), decimal=8, err_msg="Float64 square root error")

    stopMatlab(mlab)

def test_tuple():
    pass


def test_dict():
    pass


def test_array():
    pass
