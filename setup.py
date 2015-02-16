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


from distutils.core import setup


# Find the messenger binary file(s) and copy it to /matlab folder.
from messenger.get_messenger_dir import get_messenger_dir
messenger_dir = get_messenger_dir()

for f in glob.glob("./messenger/%s/messenger.*" % messenger_dir):
    shutil.copy(f, "./pymatbridge/matlab")


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
            #extras_require=EXTRAS_REQUIRE,
            scripts=BIN
            )


# Now call the actual setup function
if __name__ == '__main__':
    setup(**opts)
