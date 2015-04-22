# -*- coding: utf-8 -*-
"""
Pymatbridge: A python interface to call out to Matlab(R)
"""

import os
import sys
import filecmp
import itertools

try:
    import pkg_resources
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()

from setuptools import  setup, find_packages
from setuptools.command.test import test as TestCommand
from distutils import file_util
from distutils.extension import Extension
from pymatbridge.messenger import get_messenger_dir

from version import __version__, __build__, __release__

messenger = pkg_resources.resource_filename('pymatbridge.messenger', get_messenger_dir())
matlab    = pkg_resources.resource_filename('pymatbridge', 'matlab')
newfiles = filecmp.cmpfiles(messenger, matlab, os.listdir(messenger), shallow=False)[1:]

for binary in itertools.chain(*newfiles):
    cmd = (os.path.join(messenger, binary), os.path.join(matlab, binary))
    print('Copying %s' % binary)
    file_util.copy_file(*cmd, update=True)

extension = Extension(
    name='messenger.mexmaci',
    sources=['messenger/src/messenger.c'],
    include_dirs=['/usr/local/include'],
    library_dirs=['/usr/local/lib/'],
    libraries=['zmq'],
)

class NoseTestCommand(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import nose
        args = 'nosetests -v --exe --with-cov '
        if sys.version_info == (2, 7):
            args += '--cover-package pymatbridge'
        nose.run_exit(argv=args.split())

setup(
    name="pymatbridge",
    maintainer="Ariel Rokem",
    maintainer_email="arokem@gmail.com",
    description=__doc__,
    tests_require=['nose', 'coverage'],
    setup_requires=['wheel'],
    cmdclass={'test': NoseTestCommand},
    version=__release__,
    packages=find_packages(exclude=['tests*']),
    zip_safe = False,
    requires=['numpy', 'pyzmq'],
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
        ],
    },
)
