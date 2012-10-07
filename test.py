from pymatbridge import Matlab

# Initialise MATLAB
mlab = Matlab(matlab='/Applications/MATLAB_R2010b.app/bin/matlab')

# Start the server
mlab.start()
# Run a test function: just adds 1 to the argument a
res = []
for i in range(10):
     res.append(mlab.run('~/source/python-matlab-bridge/test.m', {'a': i})['result'])
     print res[-1]

# Stop the MATLAB server
mlab.stop()
