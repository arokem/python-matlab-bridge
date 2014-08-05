import time
import numpy as np
import numpy.testing as npt
import os.path
import pymatbridge

_dir = os.path.dirname(os.path.abspath(__file__))

mlab = pymatbridge.Matlab(matlab='/opt/matlab/R2013a/bin/matlab', log=True, capture_stdout=True)
mlab.start()

if 1:
    #conventional behaviour, perform the matlab command and return the result
    z = mlab.zeros(5)
    npt.assert_equal(z, np.zeros((5,5)))

    #perform the same command, and save the 1 output variable on the matlab side
    #with the name 'z'. return a placeholder containing some metadata about it
    placeholder = mlab.zeros(5,nout=1,saveout=('z',))
    assert placeholder == '__VAR=z|double([5 5])'
    #now return the result
    z = mlab.get_variable('z')
    npt.assert_equal(z, np.zeros((5,5)))

if 1:
    #this time the matlab command returns two variables
    x,y = mlab.meshgrid(range(1,4),range(10,15),nout=2)
    npx,npy = np.meshgrid(range(1,4),range(10,15))
    npt.assert_equal(x,npx); npt.assert_equal(y,npy)

    #perform the same command, but leave the result in matlab
    placeholder = mlab.meshgrid(range(1,4),range(10,15),nout=2,saveout=('X','Y'))
    assert placeholder == '__VAR=Y|double([5 3]);__VAR=X|double([5 3]);'

    #now return the result
    x = mlab.get_variable('X')
    npt.assert_equal(x,npx)

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

mlab.stop()
