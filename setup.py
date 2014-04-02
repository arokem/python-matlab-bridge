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
bin_location = ""
if sys.platform == "darwin":
    if not os.path.exists("./messenger/mexmaci64/messenger.mexmaci64"):
        raise ValueError("messenger.mexmaci64 is not built yet. Please build it yourself.")
    bin_location = "./messenger/mexmaci64/messenger.mexmaci64"

elif sys.platform == "linux2":
    if not os.path.exists("./messenger/mexa64/messenger.mexa64"):
        raise ValueError("messenger.mexa64 is not built yet. Please build it yourself.")
    bin_location = "./messenger/mexa64/messenger.mexa64"

elif sys.platform == "win32":
    if not os.path.exists("./messenger/mexw32/messenger.mexw32"):
        raise ValueError("messenger.mexw32 is not built yet. Please build it yourself.")
    bin_location = "./messenger/mexw32/messenger.mexw32"

else:
    raise ValueError("Known platform")

shutil.copy(bin_location, "./pymatbridge/matlab")

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
            scripts=BIN
            )


# Now call the actual setup function
if __name__ == '__main__':
    setup(**opts)
