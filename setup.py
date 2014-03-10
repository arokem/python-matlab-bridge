#!/usr/bin/env python
"""Setup file for python-matlab-bridge"""

import os
import sys

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

from distutils.core import setup

# Get version and release info, which is all stored in pymatbridge/version.py
ver_file = os.path.join('pymatbridge', 'version.py')
execfile(ver_file)

opts = dict(name=NAME,
            maintainer=MAINTAINER,
            maintainer_email=MAINTAINER_EMAIL,
            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            url=URL,
            download_url=DOWNLOAD_URL,
            license=LICENSE,
            classifiers=CLASSIFIERS,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            platforms=PLATFORMS,
            version=VERSION,
            packages=PACKAGES,
            package_data=PACKAGE_DATA,
            requires=REQUIRES,
            )

# For some commands, use setuptools.  Note that we do NOT list install here!
# If you want a setuptools-enhanced install, just run 'setupegg.py install'
needs_setuptools = set(('develop', ))
if len(needs_setuptools.intersection(sys.argv)) > 0:
    import setuptools

# Only add setuptools-specific flags if the user called for setuptools, but
# otherwise leave it alone
if 'setuptools' in sys.modules:
    opts['zip_safe'] = False

# If the user calls "python setup.py install", we call "conda install" to
# grab the package online. If the user calls "python setup.py install build-conda"
# We run the original python install. This should happen in a conda building recipe
if __name__ == '__main__':
    if (len(sys.argv) == 2):
        os.system("conda install pymatbridge")
    elif (len(sys.argv) == 3 and sys.argv[2] == "build-conda"):
        setup(**opts)
    else:
        print "Invalid option"

