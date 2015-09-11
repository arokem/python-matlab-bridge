# We first need to detect if we're being called as part of the setup.py
# procedure itself in a reliable manner.
try:
    __PYMATBRIDGE_SETUP__
except NameError:
    __PYMATBRIDGE_SETUP__ = False


if __PYMATBRIDGE_SETUP__:
    pass
else:
    from .pymatbridge import *
    from .version import __version__

    try:
        from .publish import *
    except ImportError:
        pass

    try:
        from .matlab_magic import *
    except ImportError:
        pass
