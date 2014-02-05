import pymatbridge as pymat
import random as rd
import numpy as np
import numpy.testing as npt
import test_utils as tu

class TestArray:

    # Start a Matlab session before any tests
    @classmethod
    def setup_class(cls):
        cls.mlab = tu.connect_to_matlab()

    # Tear down the Matlab session after all the tests are done
    @classmethod
    def teardown_class(cls):
        tu.stop_matlab(cls.mlab)


    # Pass a 1000*1000 array to Matlab
    def test_array_size(self):
        array = np.random.random_sample((50,50)).tolist()
        res = self.mlab.run_func("array_size.m",{'val':array})['result']
        npt.assert_almost_equal(res, array, decimal=8, err_msg = "test_array_size: error")


