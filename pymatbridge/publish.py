import IPython.nbformat.current as nbformat


def format_line(line):
    """
    Format a line of Matlab into either a markdown line or a code line.

    Parameters
    ----------
    line : str
        The line of code to be formatted. Formatting occurs according to the
        following rules:

        - If the line starts with three '%' signs, it will be converted to h1
          and we will assume that it starts a new cell. Suggested use: title.
        - If the line starts with (at least) two %% signs, a new cell will be
          started and  this line will be converted to h2. Suggested use:
          section title.
        - Additional '#' signs can be used to produce entire lines with other
          heading styles. Suggested use: knock yerself out.
        - If the line doesn't start with a '%' sign, it is assumed to be legit
          matlab code. We will continue to
    """
    if line.startswith('%%%'):
        md = True
        new_cell = True
        # Strip off the % signs:
        source = '#' + line.split('%%%')[1]
    elif line.startswith('%%'):
        md = True
        new_cell = True
        if line.endswith('%%'):
            # This is a special case that simply means break up the code here:
            source = None
        else:
            source = '##' + line.split('%%')[1]
    elif line.startswith('%'):
        md = True
        new_cell = False
        source = line.split('%')[1]
    else:
        md = False
        new_cell = False
        source = line

    return new_cell, md, source

def convert_m_file(mfile, outfile=None):
    """
    Convert a Matlab m-file into a Matlab notebook in ipynb format

    Parameters
    ----------
    mfile : string
        Full path to a matlab m file to convert

    outfile : string (optional)
        Full path to the output ipynb file

    """
    # We should only be able to read this file:
    f = file(mfile, 'r')
    cells = []
    for l in f.readlines():
        new_cell, md, source = format_line(l)
        source = l
        while not new_cell:

            if md:
                source.join(md)
            else:
                source.join(l)

        while md is not None and new_cell is False:
            source.join(md)
            new_cell, md = format_line(l)

        cells.append(nbformat.new_text_cell('markdown', source=source))

            md=False
        else:
            while l[0] != '%':
                source += l
            cells.append(nbformat.new_code_cell(input=source,
                                                language=u'matlab'))

    f.close()

    notebook = nbformat.new_notebook(
        metadata=nbformat.new_metadata(name=fname.split),
        worksheets=cells)

    if outfile is None
        outfile = fname.split('.m')[0] + '.ipynb'
    nbfile = file(outfile, 'w')
    nbformat.write(notebook, nbfile, format='ipynb')
    nbfile.close()
