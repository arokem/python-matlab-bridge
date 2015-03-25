import os
import platform

from glob import glob

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

__all__= ['get_matlab_bin']

def get_matlab_bin(config='config.ini'):
    """
    Tries to find the MATLAB bin directory independent on host platform.
    The operation of this function can be overridden by setting the MATLAB_BIN
    variable within the configuration file specified.

    Parameters
    -=========
    config:
        Relative path to configuration file

    Returns
    =======
    matlab:
        Absolute path to matlab bin directory
    """
    cfg, host = ConfigParser(), platform.system()
    cfg.read(os.path.join(__file__, config))

    programs = {
        'Darwin' : r'/Applications',
        'Windows': r'C:/Program Files',
        'Linux'  : r'/usr/local',
    }

    if cfg.has_option(host, 'MATLAB_BIN'):
        matlab = cfg.get(host, 'MATLAB_BIN')
    else:
        # Searches for Matlab bin if it's not set
        _root    = glob(r'%s/MATLAB*' % programs[host])[0]
        _version = [p for p in os.listdir(_root) if p.startswith('R20')]
        if any(_version):
            _root = r'%s/%s' % (_root, _version.pop())
        matlab   = r'%s/%s' % (_root, 'bin')

    assert os.path.isdir(matlab)

    return os.path.normpath(matlab)

