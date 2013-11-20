import pymatbridge as pymat
import random as rd
import numpy as np
import numpy.testing as npt
import test_utils as tu

def test_array_size():
    mlab = tu.connect_to_matlab()

    array = np.random.random_sample((50,50)).tolist()
    res = mlab.run_func("array_size.m",{'val':array})['result']
    npt.assert_almost_equal(res, array, decimal=8, err_msg = "test_array_size: error")

    tu.stop_matlab(mlab)

