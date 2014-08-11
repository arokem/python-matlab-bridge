import sys

PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
    unichr = chr
else:
    text_type = unicode
    unichr = unichr
