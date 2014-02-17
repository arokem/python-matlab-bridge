# Python-MATLAB(R) Bridge and ipython matlab_magic

A python interface to call out to [Matlab(R)](http://mathworks.com). Original
implementation by [Max Jaderberg](http://www.maxjaderberg.com/).

This implementation also includes an [ipython](http://ipython.org) matlab_magic
extension, which provides a much simplified interface for weaving python and
Matlab code together (requires ipython > 0.13).  


***AT PRESENT THIS MAY NOT WORK ON WINDOWS; BETA TESTERS WANTED ***

## Usage

For examples, check out the `.ipynb` files

## Installation

As pymatbridge uses [ZMQ](http://zeromq.org/) to communicate between Python and 
Matlab, ZMQ library and pyzmq have to be installed before the installation of 
pymatbridge. Please follow the procedures for your own platform. 

### Mac OS

First, download the latest version of [ZMQ library](http://zeromq.org/intro:get-the-software)
and follow the building instructions on the official page to install ZMQ to your machine.
This step will provide the header file and library file for the the building of pymatbridge.
ZMQ will be installed to the system directories on default. If you don't have permissions 
we recommend you to install ZMQ to 

	~/zmq

by using 

	./configure --prefix=~/zmq
	make
	make install
	
Next, install [pyzmq](http://zeromq.org/bindings:python) and make sure it's import-able.

Then, Create an environment variable MATLAB_PATH that points to the Matlab bin directory.

Finally, install pymatbridge. 
To install from the source-code. Download the [code zip
file](https://github.com/arokem/python-matlab-bridge/archive/master.zip). Unzip
it somewhere on your machine and then issue:

	python setup.py install

This should make the python-matlab-bridge import-able.

Alternatively, you can get pymatbridge at the
[cheese-shop](https://pypi.python.org/pypi/pymatbridge).

This means that you can use:

    easy_install pymatbridge

Or

    pip install pymatbridge

To get things going.


### Linux

TBD

### Windows

TBD

### API: 

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


