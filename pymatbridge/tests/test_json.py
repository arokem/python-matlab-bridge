import pymatbridge as pymat
import numpy.testing as npt

# Add 1 to the argument and return it
def test_demo_func():
    mlab = pymat.Matlab()
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "Connection failed")

    for i in range(5):
        res = mlab.run_func('demo_func.m', {'a': i})['result']
        ans = i + 1
        npt.assert_equal(res, ans, err_msg = "demo_func.m test failed")

    mlab.stop()
    npt.assert_(not mlab.is_connected(), msg = "Disconnection failed")

# Print some strange characters in Matlab, get them back and compare.
def test_special_character():
    mlab = pymat.Matlab()
    mlab.start()
    npt.assert_(mlab.is_connected(), msg = "Connection failed")

    # Test 1:"hi"\n
    res = mlab.run_code('fprintf(1, char([34, 104, 105, 34, 10]));')['content']['stdout']
    ans = unichr(34) + unichr(104) + unichr(105) + unichr(34) + unichr(10)
    npt.assert_equal(res, ans, err_msg = "Special Character Test 1 failed")

    # Test 2:\b\n
    res = mlab.run_code('fprintf(1, char([8,10]));')['content']['stdout']
    ans = unichr(8) + unichr(10)
    npt.assert_equal(res, ans, err_msg = "Special Character Test 2 failed")

    # Test 3:\f\n
    res = mlab.run_code('fprintf(1, char([12,10]));')['content']['stdout']
    ans = unichr(12) + unichr(10)
    npt.assert_equal(res, ans, err_msg = "Special Character Test 3 failed")

    # Test 4:\r\n
    res = mlab.run_code('fprintf(1, char([13,10]));')['content']['stdout']
    ans = unichr(13) + unichr(10)
    npt.assert_equal(res, ans, err_msg = "Special Character Test 4 failed")

    # Test 5:\t\n
    res = mlab.run_code('fprintf(1, char([9,10]));')['content']['stdout']
    ans = unichr(9) + unichr(10)
    npt.assert_equal(res, ans, err_msg = "Special Character Test 5 failed")

    # Test 6:\\\n
    res = mlab.run_code('fprintf(1, char([92,92,10]));')['content']['stdout']
    ans = unichr(92) + unichr(10)   # Python already encoded double-slash as 92
    npt.assert_equal(res, ans, err_msg = "Special Character Test 6 failed")

    # Test 7:/\n
    res = mlab.run_code('fprintf(1, char([47,10]));')['content']['stdout']
    ans = unichr(47) + unichr(10)
    npt.assert_equal(res, ans, err_msg = "Special Character Test 7 failed")

    # Test 8: Lots of strange characters
    res = mlab.run_code('fprintf(1,char([47,92,92,47,8,12,10,13,9,12,8,8,12,47,34,47,10,10,47,34]));')['content']['stdout']
    ans = unichr(47) + unichr(92) + unichr(47) + unichr(8) + unichr(12) + unichr(10) \
            + unichr(13) + unichr(9) + unichr(12) + unichr(8) + unichr(8) + unichr(12) \
            + unichr(47) + unichr(34) + unichr(47) + unichr(10) + unichr(10) + unichr(47) + unichr(34)
    npt.assert_equal(res, ans, err_msg = "Special Character Test 8 failed")

    mlab.stop()
    npt.assert_(not mlab.is_connected(), msg = "Disconnection failed")

