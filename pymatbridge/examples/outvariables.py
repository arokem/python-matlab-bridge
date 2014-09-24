import time
import numpy as np
import numpy.testing as npt
import os.path
import pymatbridge

_dir = os.path.dirname(os.path.abspath(__file__))

mlab = pymatbridge.Matlab(matlab='/opt/matlab/R2013a/bin/matlab', log=True, capture_stdout=True)
mlab.start()

if 1:
    with mlab.fig('/tmp/bob/test.png') as f:
        mlab.plot(range(1000))
        mlab.suptitle('test')
        mlab.ylabel('y label')

if 1:
    px = mlab.set_variable('v1',5)
    assert repr(px) == '<ProxyVariable __VAR=v1|double([1 1])>'
    assert str(px) == 'v1'
    assert px() == 5

if 1:
    #conventional behaviour, perform the matlab command and return the result
    z = mlab.zeros(5)
    npt.assert_equal(z, np.zeros((5,5)))

    #perform the same command, and save the 1 output variable on the matlab side
    #with the name 'z'. return a placeholder containing some metadata about it
    _z = mlab.zeros(5,nout=1,saveout=('z',))
    assert repr(_z) == '<ProxyVariable __VAR=z|double([5 5])>'

    #now return the real variable, not the proxy
    z = _z()
    npt.assert_equal(z, np.zeros((5,5)))

    #now return the result
    z = mlab.get_variable('z')
    npt.assert_equal(z, np.zeros((5,5)))

if 1:
    #this time the matlab command returns two variables
    x,y = mlab.meshgrid(range(1,4),range(10,15),nout=2)
    npx,npy = np.meshgrid(range(1,4),range(10,15))
    npt.assert_equal(x,npx); npt.assert_equal(y,npy)

    #perform the same command, but leave the result in matlab
    _x,_y = mlab.meshgrid(range(1,4),range(10,15),nout=2,saveout=('X','Y'))
    assert repr(_x) == '<ProxyVariable __VAR=X|double([5 3])>'
    assert repr(_y) == '<ProxyVariable __VAR=Y|double([5 3])>'

    #now return the real variable, not the proxy
    x = _x()
    npt.assert_equal(x,npx)

    #now return the result
    x = mlab.get_variable('X')
    npt.assert_equal(x,npx)

    #or pass the proxy to get_variable to do the same
    x = mlab.get_variable(_x)
    npt.assert_equal(x,npx)

    #now pass the proxy to a matlab command and check it decodes it
    z = mlab.cat(3,_x,_y)
    npz = np.dstack((npx,npy))
    npt.assert_equal(z,npz)

    #annother approach, mixing variables on the matlab side
    #(calling str(proxy) will return the name)
    mlab.run_code('zb=cat(3,%s,%s);' % (_x, _y))
    zb = mlab.get_variable('zb')
    npt.assert_equal(z,zb)

if 1:
    mlab.run_func(os.path.join(_dir,'example_func.m'), 'john', nout=1, saveout=('lol',))
    assert 'hello from john' == mlab.get_variable('lol')

if 1:
    mlab.run_script(os.path.join(_dir,'example_script.m'))
    q = mlab.get_variable('q')
    npt.assert_equal(q,range(1,11))
    f = mlab.get_variable('f')
    npt.assert_equal(f,45)

if 1:
    mlab.run_code('foo=1:100;')
    m = mlab.get_variable('foo')
    npt.assert_equal(m,range(1,101))

    mlab.run_code('foo=1:100;')

if 1:
    a,b = mlab.run_code("""
function [a, b] = cheese(c, d)
  a = 2;
  b = c + d;
end""", 3, 9, nout=2)
    print a
    print b

mlab.stop()
