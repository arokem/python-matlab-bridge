import os
import subprocess
import logging
import tarfile

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

__all__= ['get_matlab_env', 'fetch_zmq']

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

    return dict(env.split('=', maxsplit=1) for env in envs)

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
    print('Downloading ZMQ Source Version %i.%i.%i'      % version)
    url = ("http://download.zeromq.org/zeromq-%i.%i.%i.tar.gz" % version)
    name = urlretrieve(url, url.rsplit('/')[-1])[0]

    print('Extracting into prefix %s' % prefix)
    with tarfile.open(name) as tar:
        tar.extractall(prefix)

    print('Download Complete')
    os.remove(name)
