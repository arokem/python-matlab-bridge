import os
import platform
import subprocess
import logging
import tarfile

from glob import glob

try:
    from urllib.request import urlretrieve
    from configparser import ConfigParser
except ImportError:
    from urllib2 import urlretrieve 
    from ConfigParser import ConfigParser

__all__= ['get_matlab_bin', 'get_matlab_env', 'fetch_zmq']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def get_matlab_env(matlab='matlab'):
    """
    Get the underlying environment variables set for a matlab installation.

    Parameters
    ==========
    matlab: string
        Path to the matlab binary executable.
        If matlab is in the users $PATH, just pass 'matlab'

    Returns
    =======
    environment: dictionary
        Mapping of environment variable[s]
    """
    command = ' '.join([matlab, '-e']),
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    envs    = (line.decode('utf-8').strip() for line in process.stdout)
    mapping = (env.split('=', maxsplit=1)   for env  in envs)

    return {key:value for key, value in mapping}

def fetch_zmq(prefix, version=(4,0,5)):
    """
    Download and extract libzmq

    Parameters
    ==========
    save: str
        File Save Location
    version: tuple
        ZMQ Version Number
    """
    logger.info('Downloading ZMQ Source Version %i.%i.%i'     % version)
    url = ("http://download.zeromq.org/zeromq-%i.%i.%i.tar.gz" % version)
    name = urlretrieve(url, url.rsplit('/')[-1])[0]

    logger.info('Extracting into prefix %s' % prefix)
    with tarfile.open(name) as tar:
        tar.extractall(prefix)

    logging.info('Download Complete')
    os.remove(name)