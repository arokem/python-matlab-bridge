"""

matlab_magic
============

Magic command interface for interactive work with Matlab(R) via the pymatbridge


Note
====
Thanks to Max Jaderberg for his work on pymatbridge.

"""

import sys, os
import tempfile
from glob import glob
from shutil import rmtree
from getopt import getopt

import numpy as np
try:
    import scipy.io as sio
    has_io = True
except ImportError:
    has_io = False
    no_io_str = "Must have scipy.io to perform i/o"
    no_io_str += "operations with the Matlab session"

import IPython

ipython_version = int(IPython.__version__[0])

from IPython.core.displaypub import publish_display_data
from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic,
                                line_cell_magic, needs_local_scope)
from IPython.testing.skipdoctest import skip_doctest
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)
from IPython.utils.py3compat import str_to_unicode, unicode_to_str, PY3

import pymatbridge as pymat
from .compat import text_type


class MatlabInterperterError(RuntimeError):
    """
    Some error occurs while matlab is running
    """
    def __init__(self, line, err):
        self.line = line
        self.err = err

    def __unicode__(self):
        s = "Failed to parse and evaluate line %r.\n Matlab error message: %r"%\
                (self.line, self.err)
        return s

    if PY3:
        __str__ = __unicode__
    else:
        def __str__(self):
            return unicode_to_str(text_type(self), 'utf-8')



@magics_class
class MatlabMagics(Magics):
    """
    A set of magics for interactive work with Matlab(R).
    """
    def __init__(self, shell,
                 matlab='matlab',
                 maxtime=60,
                 pyconverter=np.asarray,
                 cache_display_data=False):
        """
        Parameters
        ----------

        shell : IPython shell

        matlab : str
            The system call to start a matlab session. Allows you to choose a
            particular version of matlab if you want

        maxtime : float
           The maximal time to wait for responses for matlab (in seconds).
           Default: 10 seconds.

        pyconverter : callable
            To be called on matlab variables returning into the ipython
            namespace

        cache_display_data : bool
            If True, the published results of the final call to R are
            cached in the variable 'display_cache'.

        """
        super(MatlabMagics, self).__init__(shell)
        self.cache_display_data = cache_display_data

        self.Matlab = pymat.Matlab(matlab, maxtime=maxtime)
        self.Matlab.start()
        self.pyconverter = pyconverter

    def __del__(self):
        """shut down the Matlab server when the object dies.

        2FIX: this seems to not be called when ipython terminates. bleah.
        """
        try:
            self.Matlab.stop()
        except:
            raise

    def eval(self, line):
        """
        Parse and evaluate a single line of matlab
        """
        run_dict = self.Matlab.run_code(line)

        if run_dict['success'] == 'false':
            raise MatlabInterperterError(line, run_dict['content']['stdout'])

        # This is the matlab stdout:
        return run_dict

    def set_matlab_var(self, name, value):
        """
        Set up a variable in Matlab workspace
        """
        run_dict = self.Matlab.set_variable(name, value)

        if run_dict['success'] == 'false':
            raise MatlabInterperterError(line, run_dict['content']['stdout'])


    @magic_arguments()
    @argument(
        '-i', '--input', action='append',
        help='Names of input variable from shell.user_ns to be assigned to Matlab variables of the same names after calling self.pyconverter. Multiple names can be passed separated only by commas with no whitespace.'
        )

    @argument(
        '-o', '--output', action='append',
        help='Names of variables to be pushed from matlab to shell.user_ns after executing cell body and applying self.Matlab.get_variable(). Multiple names can be passed separated only by commas with no whitespace.'
        )

    @argument(
        '-s', '--silent', action='store_true',
        help='Do not display text output of MATLAB command'
        )

    @argument(
        'code',
        nargs='*',
        )


    @needs_local_scope
    @line_cell_magic
    def matlab(self, line, cell=None, local_ns=None):
        """

        Execute code in matlab

        """
        args = parse_argstring(self.matlab, line)

        # arguments 'code' in line are prepended to
        # the cell lines

        if cell is None:
            code = ''
            return_output = True
            line_mode = True
        else:
            code = cell
            return_output = False
            line_mode = False

        code = ' '.join(args.code) + code

        if local_ns is None:
            local_ns = {}


        if args.input:
            if has_io:
                for input in ','.join(args.input).split(','):
                    try:
                        val = local_ns[input]
                    except KeyError:
                        val = self.shell.user_ns[input]
                    # The _Session.set_variable function which this calls
                    # should correctly detect numpy arrays and serialize them
                    # as json correctly.
                    self.set_matlab_var(input, val)

            else:
                raise RuntimeError(no_io_str)

        text_output = ''
        #imgfiles = []

        try:
            if line_mode:
                e_s = "There was an error running the code:\n %s"%line
                result_dict = self.eval(line)
            else:
                e_s = "There was an error running the code:\n %s"%code
                result_dict = self.eval(code)
        except:
            e_s += "\n-----------------------"
            e_s += "\nAre you sure Matlab is started?"
            raise RuntimeError(e_s)



        text_output += result_dict['content']['stdout']
        # Figures get saved by matlab in reverse order...
        imgfiles = result_dict['content']['figures'][::-1]
        data_dir = result_dict['content']['datadir']

        display_data = []
        if text_output and not args.silent:
            if ipython_version < 3:
                display_data.append(('MatlabMagic.matlab',
                                     {'text/plain':text_output}))
            else:
                display_data.append({'text/plain':text_output})

        for imgf in imgfiles:
            if len(imgf):
                # Store the path to the directory so that you can delete it
                # later on:
                image = open(imgf, 'rb').read()
                if ipython_version < 3:
                    display_data.append(('MatlabMagic.matlab',
                                         {'image/png':image}))
                else:
                    display_data.append({'image/png': image})

        for disp_d in display_data:
            if ipython_version < 3:
                publish_display_data(disp_d[0], disp_d[1])
            else:
                publish_display_data(disp_d)

        # Delete the temporary data files created by matlab:
        if len(data_dir):
            rmtree(data_dir)

        if args.output:
            if has_io:
                for output in ','.join(args.output).split(','):
                    self.shell.push({output:self.Matlab.get_variable(output)})
            else:
                raise RuntimeError(no_io_str)


_loaded = False
def load_ipython_extension(ip, **kwargs):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.register_magics(MatlabMagics(ip, **kwargs))
        _loaded = True

def unload_ipython_extension(ip):
    global _loaded
    if _loaded:
        magic = ip.magics_manager.registry.pop('MatlabMagics')
        magic.Matlab.stop()
        _loaded = False

