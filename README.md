# Python-MATLAB(R) Bridge and ipython matlab_magic

A python interface to call out to [Matlab(R)](http://mathworks.com). Original
implementation by [Max Jaderberg](http://www.maxjaderberg.com/).

This implementation also includes an [ipython](http://ipython.org) matlab_magic
extension, which provides a much simplified interface for weaving python and
Matlab code together (requires ipython > 0.13).  


***AT PRESENT THIS DOES NOT WORK ON WINDOWS; BETA TESTERS WANTED ***

## Usage

For examples, check out the `.ipynb` files

## Installation

Pymatbridge communicates with Matlab using zeromq. So before installing pymatbridge you 
must have [zmq](http://zeromq.org/intro:get-the-software) library and 
[pyzmq](http://zeromq.org/bindings:python) installed on your machine. If you intend to 
use the Matlab magic extension, you'll also need [IPython](http://ipython.org/install.html).
To make pymatbridge work properly, please follow the following steps. 

### Install zmq library
Please refer to the [official guide](http://zeromq.org/intro:get-the-software) on how to
build and install zmq. After zmq is installed, make sure you can find the location where
libzmq is installed. The library extension name and default location on different systems
are listed below.

| Platform      | library name  | Default locations 		 |
| ------------- | ------------- | -------------------------- |
| MacOS      	| libzmq.dylib	| /usr/lib or /usr/local/lib |
| Linux      	| libzmq.so.3	| /usr/lib or /usr/local/lib |
| Windows		| libzmq.dll	| TBD						 |

If you specified a prefix when installing zmq, the library file should be located at the
same prefix location.

After the library file is located, you need to add it to dynamic loader path on your 
machine. On MacOS, you can do this by adding the following line to your .bash_profile:

	export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Linux, add the following line to your .bash_profile:

	export LD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Windows, 

	TBD
	
### Install pyzmq
After step 1 is finished, please grab the latest version of 
[pyzmq](http://zeromq.org/bindings:python) and follow the instructions on the official 
page. Note that pymatbridge is developed with pyzmq 14.0.0 and older versions might not 
be supported. If you have an old version pyzmq, please update it. 

### Install pymatbridge
After the steps above are done, you can install pymatbridge. Download the zip file of the 
latest release. Unzip it somewhere on your machine and then issue:

	python setup.py install
	
This should make the python-matlab-bridge import-able.

## API: 

Initialize the Matlab class:

    from pymatbridge import Matlab
    mlab = Matlab()

By default the matlab executable is whatever gets called when you type `matlab`
in your terminal, the host is localhost and the port is a random unused port.

You can specify these in the following manner: 

    mlab = Matlab(matlab='/Applications/MATLAB_R2011a.app/bin/matlab',
                    host='192.168.0.1', port=5151)

Alternatively, if `matlab` is not recognized in the command-line, you can
create a [symlink](http://en.wikipedia.org/wiki/Symbolic_link) to it's
location. For example:

	  ln -s /Applications/MATLAB_R2012b.app/bin/matlab ~/bin/matlab

Making sure that your ~/bin directory is on your bash PATH variable.
	  
You can then start the MATLAB server:

    mlab.start()

which will return True once connected.

You can then run any local MATLAB function contained within a .m file of the
same name. For example, to call the function jk in jk.m:

    %% MATLAB
    function lol = jk(args)
        arg1 = args.arg1;
        arg2 = args.arg2;
        lol = arg1 + arg2;
    end

by calling:

    res = mlab.run_func('path/to/jk.m', {'arg1': 3, 'arg2': 5})
    print res['result']

which will print 8.

Or you can run some arbitrary matlab code:

    res = mlab.run_code('a=10; b=a+3')

You can shut down the MATLAB server by calling

    mlab.stop()

NB: you can call MATLAB code before the server starts by adding code to the ./matlab/startup.m file.


### Matlab magic: 

This can be used in an ipython session in the following manner:

    import pymatbridge as pymat
    ip = get_ipython()
    pymat.load_ipython_extension(ip)

These lines will automatically start the matlab session for you. Then, you can
simply decorate a line/cell with the '%matlab' or '%%matlab' decorator and
write matlab code:

    %%matlab 
    a = linspace(0.01,6*pi,100);
    plot(sin(a))
    grid on
    hold on
    plot(cos(a),'r')

### Warnings

Python communicates with Matlab via an ad-hoc webserver. This is inherently
insecure, as the Matlab instance may be directed to perform arbitrary system
calls. There is no sandboxing of any kind. Use this code at your own risk.

# Examples

An example MATLAB function and usage from Python is shown in test.py and test.m
and there. Example notebooks are in the '.ipynb' files. 


