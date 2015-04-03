Python Matlab Bridge
====================

|Build Status| |Coverage Status| |Latest Version| |License| |Join the
chat at https://gitter.im/arokem/python-matlab-bridge|

A python interface to call out to `Matlab(R) <http://mathworks.com>`__.
Original implementation by `Max
Jaderberg <http://www.maxjaderberg.com/>`__. His original repo of the
project can be found
`here <https://github.com/jaderberg/python-matlab-bridge>`__, but please
note that the development of the two repositories has significantly
diverged.

This implementation also includes an `IPython <http://ipython.org>`__
``matlab_magic`` extension, which provides a simple interface for
weaving python and Matlab code together (requires ipython > 0.13).

Installation
============

``pymatbridge`` can be installed from
`PyPI <https://pypi.python.org/pypi/pymatbridge>`__:

.. code-block:: python

    $ pip install pymatbridge  # sudo may be needed

``pymatbridge`` communicates with Matlab using zeromq. So before
installing pymatbridge you must have
`zmq <http://zeromq.org/intro:get-the-software>`__ library and
`pyzmq <http://zeromq.org/bindings:python>`__ installed on your machine.
These can be installed using

.. code-block:: python

    $ pip install pyzmq

If you intend to use the Matlab magic extension, you'll also need
`IPython <http://ipython.org/install.html>`__, as well as
`Scipy <http://scipy.org/>`__ and `Numpy <http://www.numpy.org/>`__.
These can be installed from PyPI, or using distributions such as
`Anaconda <https://store.continuum.io/cshop/anaconda/>`__ or `Enthought
Canopy <https://store.enthought.com/downloads/>`__

Note thatIPython notebooks also depend on ``pyzmq`` so if you have
IPython notebooks installed, you likely have ``pyzmq`` already.

Usage
=====

To use the pymatbridge you need to connect your python interpreter to a
Matlab session. This is done in the following manner:

.. code-block:: python

    from pymatbridge import Matlab
    mlab = Matlab()

This creates a matlab session class instance, into which you will be
able to inject code and variables, and query for results. By default,
when you use ``start``, this will open whatever gets called when you
type ``matlab`` in your Terminal, but you can also specify the location
of your Matlab application when initializing your matlab session class:

::

    mlab = Matlab(executable='/Applications/MATLAB_R2011a.app/bin/matlab')

You can then start the Matlab server, which will kick off your matlab
session, and create the connection between your Python interpreter and
this session:

.. code-block:: python

    mlab.start()

which will return True once connected.

.. code-block:: python

    results = mlab.run_code('a=1;')

Should now run that line of code and return a ``results`` dict into your
Python namespace. The ``results`` dict contains the following fields:

.. code-block:: python

    {u'content': {u'code': u'a=1',
     u'datadir': u'/private/tmp/MatlabData/',
     u'figures': [],
     u'stdout': u'\na =\n\n     1\n\n'},
     u'success': u'true'}

In this case, the variable ``a`` is available on the Python side, by
using the ``get_variable`` method:

.. code-block:: python

    mlab.get_variable('a')

You can run any MATLAB functions contained within a .m file of the same
name. For example, to call the function jk in jk.m:

.. code-block:: python

    %% MATLAB
    function lol = jk(args)
        arg1 = args.arg1;
        arg2 = args.arg2;
        lol = arg1 + arg2;
    end

you would call:

.. code-block:: python

    res = mlab.run_func('path/to/jk.m', {'arg1': 3, 'arg2': 5})
    print(res['result'])

This would print ``8``.

You can shut down the MATLAB server by calling:

.. code-block:: python

    mlab.stop()

Tip: you can execute MATLAB code at the beginning of each of your matlab
sessions by adding code to the ``~/startup.m`` file.

Octave support & caveats
~~~~~~~~~~~~~~~~~~~~~~~~

A ``pymatbridge.Octave`` class is provided with exactly the same
interface as ``pymatbridge.Matlab``:

.. code-block:: python

    from pymatbridge import Octave
    octave = Octave()

Rather than looking for ``matlab`` at the shell, this will look for
``octave``. As with ``pymatbridge.Matlab``, you can override this by
specifying the ``executable`` keyword argument.

Rather than ``~/startup.m``, Octave looks for an ``~/.octaverc`` file
for commands to execute before every session. (This is a good place to
manipulate the runtime path, for example).

Requires Version 3.8 or higher. Notice: Neither the MXE 3.8.1 nor the
Cygwin 3.8.2 version is compatible on Windows. No Windows support will
be available until a working version of Octave 3.8+ with Java support is
released.

Matlab magic:
~~~~~~~~~~~~~

The Matlab magic allows you to use pymatbridge in the context of the
IPython notebook format.

.. code-block:: python

    %load_ext pymatbridge

These lines will automatically start the matlab session for you. Then,
you can simply decorate a line/cell with the '%matlab' or '%%matlab'
decorator and write matlab code:

.. code-block:: python

    %%matlab
    a = linspace(0.01,6*pi,100);
    plot(sin(a))
    grid on
    hold on
    plot(cos(a),'r')

More examples are provided in the ``examples`` directory

Building the pymatbridge messenger from source
==============================================

The installation of ``pymatbridge`` includes a binary of a mex function
to communicate between Python and Matlab using the
`0MQ <http://zeromq.org/>`__ messaging library. This should work without
any need for compilation on most computers. However, in some cases, you
might want to build the pymatbridge messenger from source. To do so, you
will need to follow the instructions below:

Install zmq library
~~~~~~~~~~~~~~~~~~~

Please refer to the `official
guide <http://zeromq.org/intro:get-the-software>`__ on how to build and
install zmq. On Ubuntu, it is as simple as
``sudo apt-get install libzmq3-dev``. On Windows, suggest using the
following method: - Install
`MSYS2 <http://sourceforge.net/projects/msys2/>`__ - Run
``$ pacman -S make`` - From the zmq source directory, run:
``$ sh configure --prefix=$(pwd) --build=x86_64-w64-mingw32`` - Run
``$ make``.

After zmq is installed, make sure you can find the location where libzmq
is installed. The library extension name and default location on
different systems are listed below.

+------------+----------------+------------------------------+
| Platform   | library name   | Default locations            |
+============+================+==============================+
| MacOS      | libzmq.dylib   | /usr/lib or /usr/local/lib   |
+------------+----------------+------------------------------+
| Linux      | libzmq.so.3    | /usr/lib or /usr/local/lib   |
+------------+----------------+------------------------------+
| Windows    | libzmq.dll     | C:Files3.2.4                 |
+------------+----------------+------------------------------+

If you specified a prefix when installing zmq, the library file should
be located at the same prefix location.

The pymatbridge MEX extension needs to be able to locate the zmq
library. If it's in a standard location, you may not need to do
anything; if not, there are two ways to accomplish this:

Using the dynamic loader path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One option is to set an environment variable which will point the loader
to the right directory.

On MacOS, you can do this by adding the following line to your
.bash\_profile (or similar file for your shell):

.. code-block:: shell

    export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Linux, add the following line to your .bash\_profile (or similar file
for your shell):

.. code-block:: shell

    export LD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:<Path to your zmq lib directory>

On Windows, add the install location of libzmq.dll to the PATH
environment variable. On Windows 7+, typing "environment variables" into
the start menu will bring up the apporpriate Control Panel links.

Pointing the binary at the right place
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Another option is to modify the MEX binary to point to the right
location. This is preferable in that it doesn't change loader behavior
for other libraries than just the pymatbridge messenger.

On MacOS, you can do this from the root of the pymatbridge code with:

.. code-block:: shell

    install_name_tool -change /usr/local/lib/libzmq.3.dylib <Path to your zmq lib directory>/libzmq.3.dylib messenger/maci64/messenger.mexmaci64

On Linux, you can add it to the RPATH:

.. code-block:: shell

        patchelf --set-rpath <Path to your zmq lib directory> messenger/mexa64/messenger.mexa64

Install pyzmq
~~~~~~~~~~~~~

After step 1 is finished, please grab the latest version of
`pyzmq <http://zeromq.org/bindings:python>`__ and follow the
instructions on the official page. Note that pymatbridge is developed
with pyzmq 14.0.0 and older versions might not be supported. If you have
an old version of pyzmq, please update it.

Install pymatbridge
~~~~~~~~~~~~~~~~~~~

After the steps above are done, you can install pymatbridge. Download
the zip file of the latest release. Unzip it somewhere on your machine.

For Matlab:

.. code-block:: shell

    cd messenger
    # edit local.cfg in the directory for your platform
    python make.py
    cd ..
    python setup.py install

For Octave:

.. code-block:: shell

    cd messenger/octave
    # edit local_octave.cfg in the directory for your platform
    python make_octave.py
    cd ..
    python setup.py

This should make the python-matlab-bridge import-able.

Warnings
========


Python communicates with Matlab via an ad-hoc zmq messenger. This is
inherently insecure, as the Matlab instance may be directed to perform
arbitrary system calls. There is no sandboxing of any kind. Use this
code at your own risk.

.. |Build Status| image:: https://travis-ci.org/arokem/python-matlab-bridge.svg?branch=master
   :target: https://travis-ci.org/arokem/python-matlab-bridge

.. |Coverage Status| image:: https://coveralls.io/repos/arokem/python-matlab-bridge/badge.svg?branch=master
   :target: https://coveralls.io/r/arokem/python-matlab-bridge?branch=master

.. |Latest Version| image:: https://pypip.in/version/pymatbridge/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/pymatbridge/

.. |License| image:: https://pypip.in/license/pymatbridge/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/pymatbridge/

.. |Join the chat at https://gitter.im/arokem/python-matlab-bridge| image:: https://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/arokem/python-matlab-bridge?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
