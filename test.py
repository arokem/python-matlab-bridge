import pymatbridge
from pymatbridge import Matlab

# Initialise MATLAB
mlab = Matlab()

# Start the server
mlab.start()
# Run a test function: just adds 1 to the argument a
res = []
for i in range(5):
     res.append(mlab.run_func('demo_func.m', {'a': i})['result'])
     print res[-1]

# test the JSON parsing.
# quotes, and \n
res.append(mlab.run_code('fprintf(1,char([34,104,105,34,10]));'))
print res[-1]
# \b, \n
res.append(mlab.run_code('fprintf(1,char([8,10]));'))
print res[-1]
# \f, \n
res.append(mlab.run_code('fprintf(1,char([12,10]));'))
print res[-1]
# \r, \n
res.append(mlab.run_code('fprintf(1,char([13,10]));'))
print res[-1]
# \t, \n
res.append(mlab.run_code('fprintf(1,char([9,10]));'))
print res[-1]
# \\, \n
res.append(mlab.run_code('fprintf(1,char([92,92,10]));'))
print res[-1]
# /, \n
res.append(mlab.run_code('fprintf(1,char([47,10]));'))
print res[-1]

# try a whole bunch of ugly characters:
res.append(mlab.run_code('fprintf(1,char([47,92,92,47,8,12,10,13,9,12,8,8,12,47,34,47,10,10,47,34]));'))
print res[-1]

# Stop the MATLAB server
mlab.stop()
