# Python-MATLAB(R) Bridge and ipython matlab_magic

A python interface to call out to [Matlab(R)](http://mathworks.com). Original
implementation by [Max Jaderberg](http://www.maxjaderberg.com/).

This implementation also includes an [IPython](http://ipython.org) `matlab_magic`
extension, which provides a simple interface for weaving python and
Matlab code together (requires ipython > 0.13).  


## Installation

Pymatbridge communicates with Matlab using zeromq. So before installing
pymatbridge you must have [zmq](http://zeromq.org/intro:get-the-software)
library and [pyzmq](http://zeromq.org/bindings:python) installed on your
machine. If you intend to use the Matlab magic extension, you'll also need
[IPython](http://ipython.org/install.html).  To make pymatbridge work properly,
please follow the following steps.

### Install zmq library
Please refer to the [official guide](http://zeromq.org/intro:get-the-software) on how to
build and install zmq. After zmq is installed, make sure you can find the location where
libzmq is installed. The library extension name and default location on different systems
are listed below.

| Platform      | library name  | Default locations                 |
| ------------- | ------------- | --------------------------------- |
| MacOS         | libzmq.dylib	| /usr/lib or /usr/local/lib        |
| Linux         | libzmq.so.3	| /usr/lib or /usr/local/lib        |
| Windows       | libzmq.dll    | C:\Program Files\ZeroMQ 3.2.4\bin |

If you specified a prefix when installing zmq, the library file should be located at the
same prefix location.

After the library file is located, you need to add it to dynamic loader path on your 
machine. On MacOS, you can do this by adding the following line to your .bash_profile:

	export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Linux, add the following line to your .bash_profile:

	export LD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Windows, add the install location of libzmq.dll to the PATH environmental variable.
	
### Install pyzmq
After step 1 is finished, please grab the latest version of 
[pyzmq](http://zeromq.org/bindings:python) and follow the instructions on the official 
page. Note that pymatbridge is developed with pyzmq 14.0.0 and older versions might not 
be supported. If you have an old version of pyzmq, please update it. 

### Install pymatbridge
After the steps above are done, you can install pymatbridge. Download the zip file of the 
latest release. Unzip it somewhere on your machine and then issue:

	python setup.py install
	
This should make the python-matlab-bridge import-able.


## Usage

To use the pymatbridge you need to connect your python interperter to a Matlab
session. This is done in the following manner:

    from pymatbridge import Matlab
    mlab = Matlab()

This creates a matlab session class instance, into which you will be able to
inject code and variables, and query for results. By default, when you use
`start`, this will open whatever gets called when you type `matlab`
in your Terminal, but you can also specify the location of your Matlab
application when initialzing your matlab session class:  

    mlab = Matlab(matlab='/Applications/MATLAB_R2011a.app/bin/matlab')
	  
You can then start the Matlab server, which will kick off your matlab session,
and create the connection between your Python interperter and this session:

    mlab.start()

which will return True once connected.

   results = mlab.run_code('a=1;')

Should now run that line of code and return a `results` dict into your Python
namespace. The `results` dict contains the following fields:

    {u'content': {u'code': u'a=1',
     u'datadir': u'/private/tmp/MatlabData/',
     u'figures': [],
     u'stdout': u'\na =\n\n     1\n\n'},
     u'success': u'true'}

In this case, the variable `a` is available on the Python side, by using
the `get_variable` method:

    mlab.get_variable('a')
 
You can  run any MATLAB functions contained within a .m file of the
same name. For example, to call the function jk in jk.m:

    %% MATLAB
    function lol = jk(args)
        arg1 = args.arg1;
        arg2 = args.arg2;
        lol = arg1 + arg2;
    end

you would call:

    res = mlab.run_func('path/to/jk.m', {'arg1': 3, 'arg2': 5})
    print res['result']

This would print `8`.

You can shut down the MATLAB server by calling:

    mlab.stop()

Tip: you can execute MATLAB code at the beginning of each of your matlab
sessions by adding code to the `~/startup.m` file.


### Matlab magic: 

The Matlab magic allows you to use pymatbridge in the context of the IPython
notebook format.

    %load_ext pymatbridge

These lines will automatically start the matlab session for you. Then, you can
simply decorate a line/cell with the '%matlab' or '%%matlab' decorator and
write matlab code:

    %%matlab 
    a = linspace(0.01,6*pi,100);
    plot(sin(a))
    grid on
    hold on
    plot(cos(a),'r')

More examples are provided in the `examples` directory
    
### Warnings

Python communicates with Matlab via an ad-hoc zmq messenger. This is inherently
insecure, as the Matlab instance may be directed to perform arbitrary system
calls. There is no sandboxing of any kind. Use this code at your own risk.


