import pymatbridge as pymat
import random as rd
import numpy as np
import numpy.testing as npt
import test_utils as tu


class TestPrecision:

    # Start a Matlab session before running any tests
    @classmethod
    def setup_class(cls):
        cls.mlab = tu.connect_to_matlab()

    # Tear down the Matlab session after running all the tests
    @classmethod
    def teardown_class(cls):
        tu.stop_matlab(cls.mlab)


    # Pass a 64-bit floating number through the signal path
    def test_float64_roundtrip(self):
        for i in range(0,10):
            val = np.float64(rd.random())
            res = self.mlab.run_func('precision_pass.m', {'val':val})['result']
            npt.assert_almost_equal(res, val, decimal=7, err_msg="Float64 roundtrip error")

    # Add two 64-bit floating number in Matlab and return the sum
    def test_float64_sum(self):
        for i in range(0,10):
            val1 = np.float64(rd.random())
            val2 = np.float64(rd.random())

            res = self.mlab.run_func('precision_sum.m', {'val1':val1, 'val2':val2})['result']
            npt.assert_almost_equal(res, val1 + val2, decimal=7, err_msg="Float64 sum error")

    # Multiply two 64-bit floating number in Matlab and return the product
    def test_float64_multiply(self):
        for i in range(0,10):
            val1 = np.float64(rd.random())
            val2 = np.float64(rd.random())

            res = self.mlab.run_func('precision_multiply.m', {'val1':val1, 'val2':val2})['result']
            npt.assert_almost_equal(res, val1 * val2, decimal=7, err_msg="Float64 multiply error")

    # Make a division in Matlab and return the results
    def test_float64_divide(self):
        for i in range(0,10):
            val1 = np.float64(rd.random())
            val2 = np.float64(rd.random())

            res = self.mlab.run_func('precision_divide.m', {'val1':val1, 'val2':val2})['result']
            npt.assert_almost_equal(res, val1 / val2, decimal=7, err_msg="Float64 divide error")

    # Calculate the square root in Matlab and return the result
    def test_float64_sqrt(self):
        for i in range(0,10):
            val = np.float64(rd.random())

            res = self.mlab.run_func('precision_sqrt.m', {'val':val})['result']
            npt.assert_almost_equal(res, np.sqrt(val), decimal=7, err_msg="Float64 square root error")
