from django.conf import settings
from djmatlab.pymatlab import Matlab

# Check Matlab webserver is running

matlab = Matlab('http://localhost:4000' if not hasattr(settings, 'MATLAB_SERVER') else settings.MATLAB_SERVER, port=None if not hasattr(settings, 'MATLAB_SERVER_PORT') else settings.MATLAB_SERVER_PORT)
print 'djmatlab - Connected: ', matlab.is_connected()
print 'djmatlab - Function processor working: ', matlab.is_function_processor_working()


