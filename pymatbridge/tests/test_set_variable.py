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
        array = np.random.random_sample((50,50))
        res = self.mlab.run_func("array_size.m",{'val':array})['result']
        npt.assert_almost_equal(res, array, decimal=8, err_msg = "test_array_size: error")


    def test_array_content(self):
        test_array = np.random.random_integers(2, 20, (5, 10))
        self.mlab.set_variable('test', test_array)
        npt.assert_equal(self.mlab.get_variable('test'), test_array)
        test_array = np.asfortranarray(test_array)
        self.mlab.set_variable('test', test_array)
        npt.assert_equal(self.mlab.get_variable('test'), test_array)
        # force non-contiguous
        test_array = test_array[::-1]
        self.mlab.set_variable('test', test_array)
        npt.assert_equal(self.mlab.get_variable('test'), test_array)

    def test_object_array(self):
        test_array = np.array(['hello', 1])
        self.mlab.set_variable('test', test_array)
        npt.assert_equal(self.mlab.get_variable('test'), test_array)

    def test_others(self):
        self.mlab.set_variable('test', np.float(1.5))
        npt.assert_equal(self.mlab.get_variable('test'), 1.5)
        self.mlab.set_variable('test', 'hello')
        npt.assert_equal(self.mlab.get_variable('test'), 'hello')

