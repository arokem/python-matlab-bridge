import numpy.testing as npt
import pymatbridge.publish as publish
import json
import os


MFILE = os.path.join(os.path.dirname(__file__), 'test_publish.m')


def test_format_line():
    """
    Test that lines get formatted properly

    """
    npt.assert_equal(publish.format_line('%% This begins a new cell'),
                      (True, True, ' This begins a new cell\n'))

    npt.assert_equal(publish.format_line('% This should be just markdown'),
                      (False, True, ' This should be just markdown\n'))

    npt.assert_equal(publish.format_line('This is just code'),
                      (False, False, 'This is just code'))


def test_lines_to_notebook():
    """
    Test that conversion of some lines gives you a proper notebook
    """

    lines  = ["%% This is a first line\n",
              "\n",
              "% This should be in another cell\n",
              "a = 1; % This is code\n",
              "b = 2; % This is also code\n",
              "c = 3; % code in another cell\n"]

    nb = publish.lines_to_notebook(lines)

    npt.assert_equal(nb['cells'][1]['source'][0],
                     ' This is a first line\n\n')


def test_convert_mfile():
    publish.convert_mfile(MFILE)
    nb_file = MFILE.replace('.m', '.ipynb')
    with open(nb_file) as fid:
        nb = json.load(fid)
    npt.assert_equal(nb['cells'][1]['source'][0],
                     ' Experimenting with conversion from matlab to ipynb\n\n')
    os.remove(nb_file)


def test_mfile_to_lines():
    lines = publish.mfile_to_lines(MFILE)

    nb = publish.lines_to_notebook(lines)

    npt.assert_equal(nb['cells'][1]['source'][0],
                     ' Experimenting with conversion from matlab to ipynb\n\n')
