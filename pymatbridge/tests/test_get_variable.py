import pymatbridge as pymat
import numpy.testing as npt
import test_utils as tu


class TestGetVariable:

    # Start a Matlab session before running any tests
    @classmethod
    def setup_class(cls):
        cls.mlab = tu.connect_to_matlab()

    # Tear down the Matlab session after running all the tests
    @classmethod
    def teardown_class(cls):
        tu.stop_matlab(cls.mlab)


    # Set up a floating point and get it
    def test_get_float(self):
        self.mlab.run_code("a = 456345.345345")
        self.mlab.run_code("b = 0.39748e3")

        npt.assert_equal(self.mlab.get_variable('a'), 456345.345345)
        npt.assert_equal(self.mlab.get_variable('b'), 397.48)


    # Get some arrays
    def test_get_array(self):
        self.mlab.run_code("a = [1 2 3 4]")
        self.mlab.run_code("b = [1 2; 3 4]")

        npt.assert_equal(self.mlab.get_variable('a'), [[1.,2.,3.,4.]])
        npt.assert_equal(self.mlab.get_variable('b'), [[1.,2.],[3.,4.]])


    # Try to get a non-existent variable
    def test_nonexistent_var(self):
        self.mlab.run_code("clear")

        npt.assert_equal(self.mlab.get_variable('a'), None)


    # Try to get a non-existent variable with default
    def test_nonexistent_var_default(self):
        self.mlab.run_code("clear")

        npt.assert_equal(self.mlab.get_variable('a', 'some_val'), 'some_val')
