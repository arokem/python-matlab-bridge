# Python-MATLAB Bridge

A simple interface to allow Python to call MATLAB functions.

Unlike other interfaces, MATLAB only has to start once. All communication is done over a TCP server (credit to D.Kroon University of Twente for the TCP server).

## Usage

Initialize the Matlab class. You must pass in your matlab executable, e.g.

    from pymatbridge import Matlab
    mlab = Matlab(matlab='/Applications/MATLAB_R2011a.app/bin/matlab')

By default the host is localhost and the port is 4000. This can be changed, e.g.

    mlab = Matlab(matlab='/Applications/MATLAB_R2011a.app/bin/matlab',
                    host='192.168.0.1', port=5151)

You must then start the MATLAB server:

    mlab.start()

which will return True once connected.

You can then run any local MATLAB function contained within a .m file of the same name. For example, to call the function jk in jk.m:

    %% MATLAB
    function lol = jk(args)
        arg1 = args.arg1;
        arg2 = args.arg2;
        lol = arg1 + arg2;
    end

by calling:

    res = mlab.run('path/to/jk.m', {'arg1': 3, 'arg2', 5})
    print res['result']

which will print 8.

You can shut down the MATLAB server by calling

    mlab.stop()

NB: you can call MATLAB code before the server starts by adding code to the ./matlab/startup.m file.

# Example

An example MATLAB function and usage from Python is shown in test.py and test.m

Max Jaderberg 2012