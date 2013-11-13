import pymatbridge as pymat
import numpy.testing as npt
import random as rd

def test_number():
    mlab = pymat.Matlab()
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "test_number: Connection failed")

    a = 0
    b = 0
    for i in range(0, 30):
        a = a/10 + float(rd.randint(0, 9))
        b = b/10 + float(rd.randint(0, 9))
        pythonSum = a + b
        matlabSum = mlab.run_func('test_precision_sum.m',{'a':a,'b':b})['result']
        npt.assert_equal(pythonSum, matlabSum, err_msg = "test_number: Not equal")

    mlab.stop()
    npt.assert_(not mlab.is_connected(), msg = "test_number: Disconnection failed")

def test_tuple():
    pass

def test_dict():
    pass

def test_array():
    pass
