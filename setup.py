# -*- coding: utf-8 -*-
"""
Pymatbridge: A python interface to call out to Matlab(R)
"""

import os
import sys
import filecmp
import itertools
import platform

# if setupools setuptools doesnt exist install it
try:
    import pkg_resources
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    import pkg_resources

from setuptools import  setup, find_packages
from setuptools.command.test import test as TestCommand
from setuptools.command.build_ext import build_ext
from distutils import file_util

# from pymatbridge.messenger import build_matlab, get_messenger_dir

from version import __version__, __build__, __release__

# messenger = pkg_resources.resource_filename('pymatbridge.messenger', get_messenger_dir())
# matlab    = pkg_resources.resource_filename('pymatbridge', 'matlab')
# newfiles = filecmp.cmpfiles(messenger, matlab, os.listdir(messenger), shallow=False)[1:]

# for binary in itertools.chain(*newfiles):
#     cmd = (os.path.join(messenger, binary), os.path.join(matlab, binary))
#     print('Copying %s' % binary)
#     file_util.copy_file(*cmd, update=True)

class NoseTestCommand(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import nose
        args = 'nosetests -v --exe'
        if sys.version_info[0:2] == (2, 7):
            args += ' --with-cov --cover-package pymatbridge'
        nose.run_exit(argv=args.split())

class CompileMEX(build_ext):
    def run(self):
        return build_matlab(messenger='pymatbridge/messenger/src/messenger.c')

setup(
    name="pymatbridge",
    maintainer="Ariel Rokem",
    maintainer_email="arokem@gmail.com",
    description=__doc__,
    tests_require=['wheel', 'nose', 'coverage', 'ipython[all]', 'numpy', 'pyzmq'],
    setup_requires=['wheel'],
    cmdclass={
        'test': NoseTestCommand,
        'messenger': CompileMEX,
    },
    version=__release__,
    packages=find_packages(exclude=['tests*']),
    zip_safe = False,
    requires=['numpy', 'pyzmq'],
)
