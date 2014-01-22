import pymatbridge as pymat
import numpy.testing as npt
import test_utils as tu


class TestRunCode:

    # Start a Matlab session before running any tests
    @classmethod
    def setup_class(cls):
        cls.mlab = tu.connect_to_matlab()

    # Tear down the Matlab session after running all the tests
    @classmethod
    def teardown_class(cls):
        tu.stop_matlab(cls.mlab)

    # Running 'disp()' in Matlab command window
    def test_disp(self):
        result1 = self.mlab.run_code("disp('Hello world')")['content']['stdout']
        result2 = self.mlab.run_code("disp('   ')")['content']['stdout']
        result3 = self.mlab.run_code("disp('')")['content']['stdout']

        npt.assert_equal(result1, "Hello world\n")
        npt.assert_equal(result2, "   \n")
        npt.assert_equal(result3, "")

    # Make some assignments and run basic operations
    def test_basic_operation(self):
        result_assignment_a = self.mlab.run_code("a = 21.23452261")['content']['stdout']
        result_assignment_b = self.mlab.run_code("b = 347.745")['content']['stdout']
        result_sum = self.mlab.run_code("a + b")['content']['stdout']
        result_diff = self.mlab.run_code("a - b")['content']['stdout']
        result_product = self.mlab.run_code("a * b")['content']['stdout']
        result_division = self.mlab.run_code("c = a / b")['content']['stdout']


        npt.assert_equal(result_assignment_a, unicode("\na =\n\n   21.2345\n\n"))
        npt.assert_equal(result_assignment_b, unicode("\nb =\n\n  347.7450\n\n"))
        npt.assert_equal(result_sum, unicode("\nans =\n\n  368.9795\n\n"))
        npt.assert_equal(result_diff, unicode("\nans =\n\n -326.5105\n\n"))
        npt.assert_equal(result_product, unicode("\nans =\n\n   7.3842e+03\n\n"))
        npt.assert_equal(result_division, unicode("\nc =\n\n    0.0611\n\n"))

    # Put in some undefined code
    def test_undefined_code(self):
        success = self.mlab.run_code("this_is_nonsense")['success']
        message = self.mlab.run_code("this_is_nonsense")['content']['stdout']

        npt.assert_equal(success, "false")
        npt.assert_equal(message, "Undefined function or variable 'this_is_nonsense'.")
