from pymatbridge import Matlab

# Initialise MATLAB
mlab = Matlab(port=4000)
# Start the server
mlab.start()
# Run a test function: just adds 1 to the argument a
for i in range(10):
    print mlab.run('~/Sites/python-matlab-bridge/test.m', {'a': i})['result']
# Stop the MATLAB server
mlab.stop()