import pymatbridge as pymat
import numpy.testing as npt
import test_utils as tu


class TestFunctionProcessor:

    # Start a Matlab session before running any tests
    @classmethod
    def setup_class(cls):
        cls.mlab = tu.connect_to_matlab()

    # Tear down the Matlab session after running all the tests
    @classmethod
    def teardown_class(cls):
        tu.stop_matlab(cls.mlab)

    # Test the "is_function_processor_working()" function
    def test_is_function_processor_working(self):
        npt.assert_equal(self.mlab.is_function_processor_working(), True)
