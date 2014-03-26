import numpy.testing as npt
import pymatbridge.publish as publish

def test_format_line():
    """
    Test that lines get formatted properly

    """
    npt.assert_equal(publish.format_line('%% This begins a new cell'),
                      (True, True, ' This begins a new cell'))

    npt.assert_equal(publish.format_line('% This should be just markdown'),
                      (False, True, ' This should be just markdown'))

    npt.assert_equal(publish.format_line('This is just code'),
                      (False, False, 'This is just code'))

    # Special case: empty lines are interpreted as a signal to start a new
    # cell:
    npt.assert_equal(publish.format_line('\n'),
                      (True, False, ''))


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

    npt.assert_equal(nb['worksheets'][0]['cells'][0]['source'],
                     ' This is a first line\n')
