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
import pymatbridge as pymat

from IPython.core.displaypub import publish_display_data
from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic,
                                line_cell_magic, needs_local_scope)
from IPython.testing.skipdoctest import skip_doctest
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)
from IPython.utils.py3compat import str_to_unicode, unicode_to_str, PY3


    
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
            return unicode_to_str(unicode(self), 'utf-8')


def matlab_converter(matlab, key):
    """

    Reach into the matlab namespace and get me the value of the variable
    
    """
    exec('this=np.array(%s)'%matlab.get_variable(key))
    return this

@magics_class
class MatlabMagics(Magics):
    """
    A set of magics for interactive work with Matlab(R).
    """
    def __init__(self, shell,
                 matlab_converter=matlab_converter,
                 pyconverter=np.asarray,
                 cache_display_data=False):
        """
        Parameters
        ----------

        shell : IPython shell

        pyconverter : callable
            To be called on matlab variables returning into the ipython
            namespace
            
        matlab_converter : callable
            To be called on values in ipython namespace before 
            assigning to variables in matlab.

        cache_display_data : bool
            If True, the published results of the final call to R are 
            cached in the variable 'display_cache'.

        """
        super(MatlabMagics, self).__init__(shell)
        self.cache_display_data = cache_display_data

        self.Matlab = pymat.Matlab()
        self.Matlab.start()

        self.pyconverter = pyconverter
        self.matlab_converter = matlab_converter        

    def eval(self, line):
        """
        Parse and evaluate a single line of matlab
        """
        run_dict = self.Matlab.run_code(line)

        if run_dict['success'] == 'false':
            raise MatlabInterperterError(line, run_dict['content']['stdout'])

        # This is the matlab stdout: 
        return run_dict
        
    @magic_arguments()
    @argument(
        '-i', '--input', action='append',
        help='Names of input variable from shell.user_ns to be assigned to Matlab variables of the same names after calling self.pyconverter. Multiple names can be passed separated only by commas with no whitespace.'
        )

    @argument(
        '-o', '--output', action='append',
        help='Names of variables to be pushed from matlab to shell.user_ns after executing cell body and applying self.matlab_converter. Multiple names can be passed separated only by commas with no whitespace.'
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
            for input in ','.join(args.input).split(','):
                try:
                    val = local_ns[input]
                except KeyError:
                    val = self.shell.user_ns[input]
                self.eval('%s=%s;'%(input, self.pyconverter(val)))

        text_output = ''
        imgfiles = []
        
        if line_mode:
            result_dict = self.eval(line)
            text_output += result_dict['content']['stdout']
            imgfiles.append(result_dict['content']['figures'])
        else:
            result_dict = self.eval(code)
            text_output += result_dict['content']['stdout']
            imgfiles.append(result_dict['content']['figures'])

        display_data = []
        if text_output:
            display_data.append(('MatlabMagic.matlab',
                                 {'text/plain':text_output}))
        # If there are no images, we still want this variable, so that the test
        # on its length doesn't fail:
        imgdir = [] 
        for imgf in imgfiles:
            if len(imgf):
                # Store the path to the directory so that you can delete it
                # later on:
                imgdir = os.path.split(imgf)[0]
                image = open(imgf, 'rb').read() 
                display_data.append(('MatlabMagic.matlab',
                                     {'image/png': image}))

        for tag, disp_d in display_data:
            publish_display_data(tag, disp_d)

        # Delete the temporary png files created by matlab:
        if len(imgdir):
            rmtree(imgdir)
        
        if args.output:
            for output in ','.join(args.output).split(','):
                self.shell.push({output:self.matlab_converter(self.Matlab,
                                                              output)})

            
_loaded = False
def load_ipython_extension(ip):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.register_magics(MatlabMagics)
        _loaded = True
        
