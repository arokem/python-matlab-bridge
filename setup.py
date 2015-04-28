# -*- coding: utf-8 -*-
"""
Pymatbridge: A python interface to call out to Matlab(R)
"""

import os
import sys
import filecmp
import itertools
import platform

# if setuptools doesnt exist install it
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

from pymatbridge.messenger import build_matlab, get_messenger_dir

from version import __version__, __build__, __release__

# messenger = pkg_resources.resource_filename('pymatbridge.messenger', get_messenger_dir())
# matlab    = pkg_resources.resource_filename('pymatbridge', 'matlab')
# newfiles = filecmp.cmpfiles(messenger, matlab, os.listdir(messenger), shallow=False)[1:]

# for binary in itertools.chain(*newfiles):
#     cmd = (os.path.join(messenger, binary), os.path.join(matlab, binary))
#     print('Copying %s' % binary)
#     file_util.copy_file(*cmd, update=True)

def read(*files):
    """
    Takes an arbitrary number of file names based from the package root
    returns their contents concatenated with two newlines.
    """
    return '\n\n'.join([open(f, 'rt').read() for f in files if os.path.isfile(f)])


class NoseTestCommand(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import nose
        args = 'nosetests -v --exe'
        if sys.version_info[0:2] == (2, 7):
            args += ' '
            args += '--with-cov --cover-package pymatbridge'
        nose.run_exit(argv=args.split())

class CompileMEX(build_ext):
    def run(self):
        return build_matlab(messenger='pymatbridge/messenger/src/messenger.c')

setup(
    name="pymatbridge",
    maintainer="Ariel Rokem",
    maintainer_email="arokem@gmail.com",
    description=__doc__,
    long_description=read('README.md', 'LICENSE'),
    tests_require=['ipython', 'nose', 'coverage', 'numpy', 'pyzmq'],
    setup_requires=['wheel'],
    cmdclass={
        'test': NoseTestCommand,
        'messenger': CompileMEX,
    },
    license=read('LICENSE'),
    scripts='scripts/publish-notebook',
    version=__release__,
    packages=find_packages(exclude=['tests*']),
    zip_safe=False,
    requires=['pyzmq', 'numpy'],
    keywords='matlab python packaging',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Build Tools',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Other Scripting Engines',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
    ],
)
