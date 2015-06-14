import os

import pymatbridge as pymat
from pymatbridge.compat import text_type
import numpy as np
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
        if tu.on_octave():
            npt.assert_equal(result3, '\n')
        else:
            npt.assert_equal(result3, "")

    # Make some assignments and run basic operations
    def test_basic_operation(self):
        result_assignment_a = self.mlab.run_code("a = 21.23452261")['content']['stdout']
        result_assignment_b = self.mlab.run_code("b = 347.745")['content']['stdout']
        result_sum = self.mlab.run_code("a + b")['content']['stdout']
        result_diff = self.mlab.run_code("a - b")['content']['stdout']
        result_product = self.mlab.run_code("a * b")['content']['stdout']
        result_division = self.mlab.run_code("c = a / b")['content']['stdout']

        if tu.on_octave():
            npt.assert_equal(result_assignment_a, text_type("a =  21.235\n"))
            npt.assert_equal(result_assignment_b, text_type("b =  347.75\n"))
            npt.assert_equal(result_sum, text_type("ans =  368.98\n"))
            npt.assert_equal(result_diff, text_type("ans = -326.51\n"))
            npt.assert_equal(result_product, text_type("ans =  7384.2\n"))
            npt.assert_equal(result_division, text_type("c =  0.061063\n"))
        else:
            npt.assert_equal(result_assignment_a, text_type("\na =\n\n   21.2345\n\n"))
            npt.assert_equal(result_assignment_b, text_type("\nb =\n\n  347.7450\n\n"))
            npt.assert_equal(result_sum, text_type("\nans =\n\n  368.9795\n\n"))
            npt.assert_equal(result_diff, text_type("\nans =\n\n -326.5105\n\n"))
            npt.assert_equal(result_product, text_type("\nans =\n\n   7.3842e+03\n\n"))
            npt.assert_equal(result_division, text_type("\nc =\n\n    0.0611\n\n"))

    # Put in some undefined code
    def test_undefined_code(self):
        success = self.mlab.run_code("this_is_nonsense")['success']
        message = self.mlab.run_code("this_is_nonsense")['content']['stdout']

        assert not success
        if tu.on_octave():
            npt.assert_equal(message, "'this_is_nonsense' undefined near line 1 column 1")
        else:
            npt.assert_equal(message, "Undefined function or variable 'this_is_nonsense'.")

    def test_stack_traces(self):
        this_dir = os.path.abspath(os.path.dirname(__file__))
        test_file = os.path.join(this_dir, 'test_stack_trace.m')

        self.mlab.run_code("addpath('%s')" % this_dir)
        response = self.mlab.run_code('test_stack_trace(10)')
        npt.assert_equal(response['stack'], [
            {'name': 'baz', 'line': 14, 'file': test_file},
            {'name': 'bar', 'line': 10, 'file': test_file},
            {'name': 'foo', 'line': 6, 'file': test_file},
            {'name': 'test_stack_trace', 'line': 2, 'file': test_file}
        ])

        response = self.mlab.run_code('x = 2')
        npt.assert_equal(response['stack'], [])
