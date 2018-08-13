"""
Setup for submit-and-compare xblock
Note: The tox testing environemnt depends on version 0.1.2 of opaque_keys,
which is not available on PyPi. The dependency is included in
requirements.txt to match the version used Stanford-Online's
fork of edx-platform.
"""


import os
from setuptools import setup
from setuptools.command.test import test as TestCommand

def package_data(pkg, root):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for dirname, _, files in os.walk(os.path.join(pkg, root)):
        for fname in files:
            data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

setup(
    name='xblock-submit-and-compare',
    version='0.6.2',
    description='Submit and Compare XBlock for self assessment',
    packages=[
        'submit_and_compare',
    ],
    install_requires=[
        'coverage',
        'django',
        'django_nose',
        'mako',
        'mock',
        'XBlock',
        'xblock-utils',
    ],
    dependency_links=[
        'https://github.com/edx/xblock-utils/tarball/c39bf653e4f27fb3798662ef64cde99f57603f79#egg=xblock-utils',
    ],
    entry_points={
        'xblock.v1': [
            'submit-and-compare = submit_and_compare:SubmitAndCompareXBlock',
        ]
    },
    package_dir={
        'submit_and_compare': 'submit_and_compare',
    },
    package_data=package_data("submit_and_compare", "static"),
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
