try:
    import nbformat.v4 as nbformat
    from nbformat import write as nbwrite
except ImportError:
    import IPython.nbformat.v4 as nbformat
    from IPython.nbformat import write as nbwrite

import numpy as np


def format_line(line):
    """
    Format a line of Matlab into either a markdown line or a code line.

    Parameters
    ----------
    line : str
        The line of code to be formatted. Formatting occurs according to the
        following rules:

        - If the line starts with (at least) two %% signs, a new cell will be
          started.

        - If the line doesn't start with a '%' sign, it is assumed to be legit
          matlab code. We will continue to add to the same cell until reaching
          the next comment line
    """
    if line.startswith('%%'):
        md = True
        new_cell = True
        source = line.split('%%')[1] + '\n'  # line-breaks in md require a line
                                             # gap!

    elif line.startswith('%'):
        md = True
        new_cell = False
        source = line.split('%')[1] + '\n'

    else:
        md = False
        new_cell = False
        source = line


    return new_cell, md, source


def mfile_to_lines(mfile):
    """
    Read the lines from an mfile

    Parameters
    ----------
    mfile : string
        Full path to an m file
    """
    # We should only be able to read this file:
    with open(mfile) as fid:
        return fid.readlines()


def lines_to_notebook(lines, name=None):
    """
    Convert the lines of an m file into an IPython notebook

    Parameters
    ----------
    lines : list
        A list of strings. Each element is a line in the m file

    Returns
    -------
    notebook : an IPython NotebookNode class instance, containing the
    information required to create a file


    """
    source = []
    md = np.empty(len(lines), dtype=object)
    new_cell = np.empty(len(lines), dtype=object)
    for idx, l in enumerate(lines):
        new_cell[idx], md[idx], this_source = format_line(l)
        # Transitions between markdown and code and vice-versa merit a new
        # cell, even if no newline, or "%%" is found. Make sure not to do this
        # check for the very first line!
        if idx>1 and not new_cell[idx]:
            if md[idx] != md[idx-1]:
                new_cell[idx] = True

        source.append(this_source)
    # This defines the breaking points between cells:
    new_cell_idx = np.hstack([np.where(new_cell)[0], -1])

    # Listify the sources:
    cell_source = [source[new_cell_idx[i]:new_cell_idx[i+1]]
                   for i in range(len(new_cell_idx)-1)]
    cell_md = [md[new_cell_idx[i]] for i in range(len(new_cell_idx)-1)]
    cells = []

    # Append the notebook with loading matlab magic extension
    notebook_head = "import pymatbridge as pymat\n" + "ip = get_ipython()\n" \
                    + "pymat.load_ipython_extension(ip)"
    cells.append(nbformat.new_code_cell(notebook_head))#, language='python'))

    for cell_idx, cell_s in enumerate(cell_source):
        if cell_md[cell_idx]:
            cells.append(nbformat.new_markdown_cell(cell_s))
        else:
            cell_s.insert(0, '%%matlab\n')
            cells.append(nbformat.new_code_cell(cell_s))#, language='matlab'))

    #ws = nbformat.new_worksheet(cells=cells)
    notebook = nbformat.new_notebook(cells=cells)
    return notebook


def convert_mfile(mfile, outfile=None):
    """
    Convert a Matlab m-file into a Matlab notebook in ipynb format

    Parameters
    ----------
    mfile : string
        Full path to a matlab m file to convert

    outfile : string (optional)
        Full path to the output ipynb file

    """
    lines = mfile_to_lines(mfile)
    nb = lines_to_notebook(lines)
    if outfile is None:
        outfile = mfile.split('.m')[0] + '.ipynb'
    with open(outfile, 'w') as fid:
        nbwrite(nb, fid)
