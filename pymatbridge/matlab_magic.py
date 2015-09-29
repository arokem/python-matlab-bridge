"""

matlab_magic
============

Magic command interface for interactive work with Matlab(R) via the pymatbridge

"""

from shutil import rmtree

import numpy as np
import IPython

from IPython.core.displaypub import publish_display_data
from IPython.core.magic import (Magics, magics_class,
                                line_cell_magic, needs_local_scope)
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)
from IPython.utils.py3compat import unicode_to_str, PY3

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
                 pyconverter=np.asarray,
                 **kwargs):
        """
        Parameters
        ----------

        shell : IPython shell

        matlab : str
            The system call to start a matlab session. Allows you to choose a
            particular version of matlab if you want

        pyconverter : callable
            To be called on matlab variables returning into the ipython
            namespace

        kwargs: additional key-word arguments to pass to initialization of
            the Matlab/Octave process
        """
        super(MatlabMagics, self).__init__(shell)

        if 'octave' in matlab.lower():
            self.Matlab = pymat.Octave(matlab, **kwargs)
        else:
            self.Matlab = pymat.Matlab(matlab, **kwargs)
        self.Matlab.start()
        self.pyconverter = pyconverter

    def eval(self, line):
        """
        Parse and evaluate a single line of matlab
        """
        run_dict = self.Matlab.run_code(line)

        if not run_dict['success']:
            raise MatlabInterperterError(line, run_dict['content']['stdout'])

        # This is the matlab stdout:
        return run_dict

    def set_matlab_var(self, name, value):
        """
        Set up a variable in Matlab workspace
        """
        run_dict = self.Matlab.set_variable(name, value)

        if not run_dict['success']:
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
        '-S', '--size', action='store', default='512,384',
        help='Pixel size of plots, "width,height.'
    )

    @argument(
        '-g', '--gui', action='store_true',
        help='Show plots in a graphical user interface'
    )

    @argument(
        'code',
        nargs='*',
        )


    @needs_local_scope
    @line_cell_magic
    def matlab(self, line, cell=None, local_ns=None):
        "Execute code in matlab."

        args = parse_argstring(self.matlab, line)
        code = line if cell is None else ' '.join(args.code) + cell

        if local_ns is None:
            local_ns = {}

        width, height = args.size.split(',')
        self.Matlab.set_plot_settings(width, height, not args.gui)

        if args.input:
            for input in ','.join(args.input).split(','):
                try:
                    val = local_ns[input]
                except KeyError:
                    val = self.shell.user_ns[input]
                # The _Session.set_variable function which this calls
                # should correctly detect numpy arrays and serialize them
                # as json correctly.
                self.set_matlab_var(input, val)

        try:
            result_dict = self.eval(code)
        except MatlabInterperterError:
            raise
        except:
            raise RuntimeError('\n'.join([
                "There was an error running the code:",
                code,
                "-----------------------",
                "Are you sure Matlab is started?",
            ]))

        text_output = result_dict['content']['stdout']
        # Figures get saved by matlab in reverse order...
        imgfiles = result_dict['content']['figures'][::-1]
        data_dir = result_dict['content']['datadir']

        display_data = []
        if text_output and not args.silent:
            display_data.append(('MatlabMagic.matlab',
                                 {'text/plain': text_output}))

        for imgf in imgfiles:
            if len(imgf):
                # Store the path to the directory so that you can delete it
                # later on:
                with open(imgf, 'rb') as fid:
                    image = fid.read()
                display_data.append(('MatlabMagic.matlab',
                                     {'image/png': image}))

        for disp_d in display_data:
            publish_display_data(source=disp_d[0], data=disp_d[1])

        # Delete the temporary data files created by matlab:
        if len(data_dir):
            rmtree(data_dir)

        if args.output:
            for output in ','.join(args.output).split(','):
                self.shell.push({output:self.Matlab.get_variable(output)})


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
