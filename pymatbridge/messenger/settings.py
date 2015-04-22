import os
import subprocess
import tarfile

try: # Python 3 Compat
    from urllib.request import urlretrieve
    string = str
except ImportError:
    from urllib import urlretrieve
    import string

__all__= ['get_matlab_env', 'fetch_zmq']


def get_matlab_env(matlab='matlab'):
    """
    Get the underlying environment variables set for a matlab installation.

    Parameters
    ----------
    matlab: str
        Path to the matlab binary executable.
        If matlab is in the users $PATH, just pass 'matlab'

    Returns
    -------
    environment: dict
        Mapping of environment variable
    """
    command = ' '.join([matlab, '-e']),
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    envs    = (line.decode('utf-8').strip() for line in process.stdout)

    return dict(string.split(env, '=', maxsplit=1) for env in envs)


def fetch_zmq(prefix, version=(4,0,5)):
    """
    Download and extract libzmq into `prefix`

    Parameters
    ----------
    save: str
        File Save Location
    version: 3-tuple
        ZMQ Version Number
    """
    print('Downloading ZMQ Source Version %i.%i.%i' % version)
    url = ("http://download.zeromq.org/zeromq-%i.%i.%i.tar.gz" % version)
    name = urlretrieve(url, url.rsplit('/')[-1])[0]

    print('Extracting into prefix %s' % prefix)
    with tarfile.open(name) as tar:
        tar.extractall(prefix)

    print('Download Complete')
    os.remove(name)
