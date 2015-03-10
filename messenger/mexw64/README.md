Dynamically linked building instructions
----------------------------------------

1) Install zeromq from the website: http://zeromq.org/distro:microsoft-windows

2) Rename one of the lib/libzmq-*.lib files to libzmq.lib in the ZeroMQ
   installation directory

3) Add the ZeroMQ bin directory to your path.

4) Edit the messenger/mexw64/local.cfg file in messenger to point to the
   zeromq install directory (you will need to update both ZMQ_INC and ZMQ_LIB).
   Also ensure the MATLAB directory is correct.

5) Run ```make.py matlab``` in the messenger directory. This should build
   messenger.mexw64

Statically linked building instructions
---------------------------------------

A statically linked library has the advantage of not requiring libzmq.dll to
be found in the path. For this reason, including it in the installer results
in a simpler and more robust installation process. While building a statically
linked mex is simple in practice, but because zeromq (as of 3/10/15) does not
provide a .lib for static linking with the windows installer, you will need to
compile this yourself. These directions are from zeromq 4.0.5.

1) Download and unzip the zeromq zip file (listed as Windows sources) from
   http://zeromq.org/intro:get-the-software
   
2) In the builds/msvc directory open the msvc.sln file in Visual Studio.

3) Create a new Platform for x64. In the Librarian section of properties, set
   the target section to /Machine:X64

4) Build libzmq with the "StaticRelease" for x64.

5) Edit the messenger/mexw64/local.cfg file to point to where you built ZeroMQ
   and your MATLAB bin directory.

6) Build messenger.mexw64 with ```make matlab --static```
