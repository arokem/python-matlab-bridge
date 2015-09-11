#!/usr/bin/env python
"""Setup file for python-matlab-bridge"""

import os
import sys
import shutil
import glob


# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

# we need some code from inside the package to build it. use the same hack as
# numpy to selectively import even if we don't have dependencies installed
if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins.__PYMATBRIDGE_SETUP__ = True
# Find the messenger binary file(s) and copy it to /matlab folder.
from pymatbridge.messenger.make import get_messenger_dir
messenger_dir = get_messenger_dir()

for f in glob.glob("./pymatbridge/messenger/%s/messenger.*" % messenger_dir):
    shutil.copy(f, "./pymatbridge/matlab")

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Get version and release info, which is all stored in pymatbridge/version.py
ver_file = os.path.join('pymatbridge', 'version.py')
exec(open(ver_file).read())

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
            extras_require=EXTRAS_REQUIRE,
            scripts=BIN
            )


# Now call the actual setup function
if __name__ == '__main__':
    setup(**opts)
