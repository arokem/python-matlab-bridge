# -*- coding: utf-8 -*-
"""
Pymatbridge: A python interface to call out to Matlab(R)
"""
import os
import shutil
import glob

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

# Set Version Info
exec(open('pymatbridge/__version__.py').read())

try:
    from setuptools import  setup
except ImportError:
    from distutils.core import setup

# Find the messenger binary file(s) and copy it to /matlab folder.
from messenger.make import get_messenger_dir

for f in glob.glob("messenger/%s/messenger.*" % get_messenger_dir()):
    shutil.copy(f, 'pymatbridge/matlab/')

# Now call the actual setup function
if __name__ == '__main__':
    setup(
        name="pymatbridge",
        maintainer="Ariel Rokem",
        maintainer_email="arokem@gmail.com",
        description=__doc__,
        long_description=open('LICENSE').read(),
        url="https://github.com/arokem/python-matlab-bridge",
        download_url="https://github.com/arokem/python-matlab-bridge/archive/master.tar.gz",
        license='BSD',
        author="https://github.com/arokem/python-matlab-bridge/contributors",
        author_email="arokem@gmail.com",
        platforms="OS Independent",
        version='.'.join([__version__, __build__]),
        packages=['pymatbridge'],
        package_data={
            "pymatbridge": [
                "matlab/matlabserver.m", "matlab/messenger.*",
                "matlab/usrprog/*", "matlab/util/*.m",
                "matlab/util/json_v0.2.2/LICENSE",
                "matlab/util/json_v0.2.2/README.md",
                "matlab/util/json_v0.2.2/test/*",
                "matlab/util/json_v0.2.2/json/*.m",
                "matlab/util/json_v0.2.2/json/java/*",
                "tests/*.py", "examples/*.ipynb"
            ]
        },
        zip_safe=False,
        requires=['pyzmq'],
        scripts=['scripts/publish-notebook'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Scientific/Engineering",
        ],
        #extras_require=['numpy', 'scipy', 'ipython']
    )
