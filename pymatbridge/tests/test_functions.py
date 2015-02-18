import numpy as np
import numpy.testing as npt
import test_utils as tu


class TestFunctions(object):

    # Start a Matlab session before running any tests
    @classmethod
    def setup_class(cls):
        cls.mlab = tu.connect_to_matlab()

    # Tear down the Matlab session after running all the tests
    @classmethod
    def teardown_class(cls):
        tu.stop_matlab(cls.mlab)

    def test_nargout(self):
        res  = self.mlab.run_func('svd', np.array([[1,2],[1,3]]), nargout=3)
        U, S, V = res['result']
        npt.assert_almost_equal(U, np.array([[-0.57604844, -0.81741556],
                                             [-0.81741556, 0.57604844]]))

        npt.assert_almost_equal(S, np.array([[ 3.86432845, 0.],
                                             [ 0., 0.25877718]]))

        npt.assert_almost_equal(V, np.array([[-0.36059668, -0.93272184],
                                             [-0.93272184, 0.36059668]]))

        res = self.mlab.run_func('svd', np.array([[1,2],[1,3]]), nargout=1)
        s = res['result']
        npt.assert_almost_equal(s, [[ 3.86432845], [ 0.25877718]])

        res = self.mlab.run_func('close', 'all', nargout=0)
        assert res['result'] == []

    def test_tuple_args(self):
        res = self.mlab.run_func('ones', (1, 2))
        npt.assert_almost_equal(res['result'], [[1, 1]])

        res = self.mlab.run_func('chol',
                                 np.array([[2, 2], [1, 1]]), 'lower')
        npt.assert_almost_equal(res['result'],
                                [[1.41421356, 0.],
                                 [0.70710678, 0.70710678]])

    def test_create_func(self):
        test = self.mlab.ones(3)
        npt.assert_array_equal(test['result'], np.ones((3, 3)))
        doc = self.mlab.zeros.__doc__
        assert 'zeros' in doc

    def test_pass_kwargs(self):
        resp = self.mlab.run_func('plot', [1, 2, 3], Linewidth=3)
        assert resp['success']
        assert len(resp['content']['figures'])
        resp = self.mlab.plot([1, 2, 3], Linewidth=3)
        assert resp['result'] is not None
        assert len(resp['content']['figures'])
