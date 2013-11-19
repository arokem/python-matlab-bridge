import pymatbridge as pymat
import random as rd
import numpy as np
import numpy.testing as npt
import test_utils as tu

# Pass a 64-bit floating number through the signal path
def testFloat64Roundtrip():
    mlab = tu.connect_to_matlab()

    for i in range(0,10):
        val = np.float64(rd.random())
        res = mlab.run_func('precision_pass.m',{'val':val})['result']
        npt.assert_almost_equal(res, val, decimal=8, err_msg="Float64 roundtrip error")

    tu.stop_matlab(mlab)


# Add two 64-bit floating number in Matlab and return the sum
def testFloat64Sum():
    mlab = tu.connect_to_matlab()

    for i in range(0,10):
        val1 = np.float64(rd.random())
        val2 = np.float64(rd.random())

        res = mlab.run_func('precision_sum.m',{'val1':val1,'val2':val2})['result']
        npt.assert_almost_equal(res, val1 + val2, decimal=8, err_msg="Float64 sum error")

    tu.stop_matlab(mlab)


# Multiply two 64-bit floating number in Matlab and return the product
def testFloat64Multiply():
    mlab = tu.connect_to_matlab()

    for i in range(0,10):
        val1 = np.float64(rd.random())
        val2 = np.float64(rd.random())

        res = mlab.run_func('precision_multiply.m',{'val1':val1,'val2':val2})['result']
        npt.assert_almost_equal(res, val1 * val2, decimal=8, err_msg="Float64 multiply error")

    tu.stop_matlab(mlab)


# Make a division in Matlab and return the results
def testFloat64Divide():
    mlab = tu.connect_to_matlab()

    for i in range(0,10):
        val1 = np.float64(rd.random())
        val2 = np.float64(rd.random())

        res = mlab.run_func('precision_divide.m',{'val1':val1,'val2':val2})['result']
        npt.assert_almost_equal(res, val1 / val2, decimal=8, err_msg="Float64 divide error")

    tu.stop_matlab(mlab)


# Calculate the square root in Matlab and return the result
def testFloat64Sqrt():
    mlab = tu.connect_to_matlab()

    for i in range(0,10):
        val = np.float64(rd.random())

        res = mlab.run_func('precision_sqrt.m',{'val':val})['result']
        npt.assert_almost_equal(res, np.sqrt(val), decimal=8, err_msg="Float64 square root error")

    tu.stop_matlab(mlab)

def test_tuple():
    pass


def test_dict():
    pass


def test_array():
    pass
