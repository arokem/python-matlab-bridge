#!/usr/bin/env python
"""Setup file for python-matlab-bridge"""

import os
import sys
import shutil

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

from distutils.core import setup

# Find the messenger binary file and copy it to /matlab folder.

def copy_bin(bin_path):
    if os.path.exists(bin_path):
        shutil.copy(bin_path, "./pymatbridge/matlab")
        return True
    else:
        return False

if sys.platform == "win32":
    raise ValueError("pymatbridge does not work on win32")
else:
    for copy_this in ["./messenger/mexmaci64/messenger.mexmaci64",
                      "./messenger/mexa64/messenger.mexa64",
                      "./messenger/mexw64/messenger.mexw64"]:
        copy_bin(copy_this)
        
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
            scripts=BIN
            )


# Now call the actual setup function
if __name__ == '__main__':
    setup(**opts)
