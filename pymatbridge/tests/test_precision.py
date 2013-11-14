import pymatbridge as pymat
import numpy.testing as npt
import random as rd

def test_number():
    mlab = pymat.Matlab()
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "test_number: Connection failed")

    a = 0
    b = 0
    for i in range(0, 20):
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
    mlab = pymat.Matlab()
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "test_dict: Connection failed")

    res = mlab.run_func("demo_dict.m",{'pDict':[{'apple':1.2,'pear':2.4,'banana':3.3}]})['result']
    npt.assert_equal(res[0], 1.2, err_msg = "value1 not equal")
    npt.assert_equal(res[1], 2.4, err_msg = "value2 not equal")
    npt.assert_equal(res[2], 3,3, err_msg = "value3 not equal")

    mlab.stop()
    npt.assert_(not mlab.is_connected(), msg = "test_dict: Disconnection failed")
def test_array():
    pass
