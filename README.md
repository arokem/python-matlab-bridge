# Python-MATLAB(R) Bridge and ipython matlab_magic

A python interface to call out to [Matlab(R)](http://mathworks.com). Original
implementation by [Max Jaderberg](http://www.maxjaderberg.com/)

This implementation also includes an [ipython](http://ipython.org) matlab_magic
extension, which provides a much simplified interface for weaving python and
Matlab code together.  


***AT PRESENT THIS DOES NOT WORK ON WINDOWS***

## Usage

For examples, check out the `.ipynb` files

### API: 

Initialize the Matlab class:

    from pymatbridge import Matlab
    mlab = Matlab()

By default the matlab executable is whatever gets called when you type 'matlab'
in your terminal, the host is localhost and the port is a random unused port.

You can specify these in the following manner: 

    mlab = Matlab(matlab='/Applications/MATLAB_R2011a.app/bin/matlab',
                    host='192.168.0.1', port=5151)

You must then start the MATLAB server:

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

# Examples

An example MATLAB function and usage from Python is shown in test.py and test.m
and there. Example notebooks are in the '.ipynb' files. 


Max Jaderberg 2012
Ariel Rokem 2012


