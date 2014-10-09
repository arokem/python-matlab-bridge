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

The pymatbridge MEX extension needs to be able to locate the zmq library. If it's in a
standard location, you may not need to do anything; if not, there are two ways to
accomplish this:

#### Using the dynamic loader path

One option is to set an environment variable which will point the loader to the right
directory.

On MacOS, you can do this by adding the following line to your .bash_profile (or similar
file for your shell):

	export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Linux, add the following line to your .bash_profile (or similar file for your shell):

	export LD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Windows, add the install location of libzmq.dll to the PATH environment variable.
On Windows 7+, typing "environment variables" into the start menu will bring up the
apporpriate Control Panel links.

#### Pointing the binary at the right place

Another option is to modify the MEX binary to point to the right location. This is
preferable in that it doesn't change loader behavior for other libraries than just
the pymatbridge messenger.

On MacOS, you can do this from the root of the pymatbridge code with:

	install_name_tool -change /usr/local/lib/libzmq.3.dylib <Path to your zmq lib directory>/libzmq.3.dylib messenger/maci64/messenger.mexmaci64

On Linux, you can add it to the RPATH:

        patchelf --set-rpath <Path to your zmq lib directory> messenger/mexa64/messenger.mexa64
	
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

To use the pymatbridge you need to connect your python interpreter to a Matlab
session. This is done in the following manner:

    from pymatbridge import Matlab
    mlab = Matlab()

This creates a matlab session class instance, into which you will be able to
inject code and variables, and query for results. By default, when you use
`start`, this will open whatever gets called when you type `matlab`
in your Terminal, but you can also specify the location of your Matlab
application when initializing your matlab session class:  

    mlab = Matlab(executable='/Applications/MATLAB_R2011a.app/bin/matlab')
	  
You can then start the Matlab server, which will kick off your matlab session,
and create the connection between your Python interpreter and this session:

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
 
You can run any MATLAB functions contained within a .m file of the
same name. For example, to call the function jk in jk.m:

    %% MATLAB
    function lol = jk(args)
        arg1 = args.arg1;
        arg2 = args.arg2;
        lol = arg1 + arg2;
    end

you would call:

    res = mlab.run_func('path/to/jk.m', {'arg1': 3, 'arg2': 5})
    print(res['result'])

This would print `8`.

You can shut down the MATLAB server by calling:

    mlab.stop()

Tip: you can execute MATLAB code at the beginning of each of your matlab
sessions by adding code to the `~/startup.m` file.

### Octave support & caveats

A `pymatbridge.Octave` class is provided with exactly the same interface
as `pymatbridge.Matlab`:

    from pymatbridge import Octave
    octave = Octave()

Rather than looking for `matlab` at the shell, this will look for `octave`.
As with `pymatbridge.Matlab`, you can override this by specifying the
`executable` keyword argument.

There are a few caveats to note about Octave support:

* `pymatbridge.Matlab` invokes MATLAB with command line options that suppress
the display of figures -- these are instead saved to image files, accessible
via `results['content']['figures']` in the results dict. No such mechanism
seems to be available for Octave, so when drawing figures you'll likely see
them briefly pop up and disappear. (If you know of a way around this, feel
free to send a pull request).
* The zmq messenger used to communicate with the Octave session is written in C
and needs to be compiled. For MATLAB various prebuilt binaries are provided
and added to MATLAB's runtime path, but as of this writing the same isn't
true for Octave. You'll need to compile the messenger (in
`messenger/src/messenger.c`) using an incantation like
`mkoctfile --mex -lzmq messenger.c` and place the resulting `messenger.mex`
file somewhere in Octave's runtime path.

Finally, rather than `~/startup.m`, Octave looks for an `~/.octaverc` file for
commands to execute before every session. (This is a good place to manipulate
the runtime path, for example).

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


