#!/usr/bin/env python

import os
import sys

import om

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = ['om', 'om.utils']
requires = ['paramiko']
scripts = ['bin/om']

with open('README.md') as f:
    readme = f.read()

setup(
    name='om',
    version=om.__version__,
    description='Collect usage for remote boxes without configuration.',
    long_description=readme,
    author='Andre Dieb Martins, Thiago Sousa Santos',
    author_email='andre.dieb@gmail.com, thiagossantos@gmail.com',
    url='http://github.com/overseer-monitoring/om',
    packages=packages,
    package_data={'': ['LICENSE', 'README.md']},
    package_dir={'om': 'om'},
    scripts=scripts,
    include_package_data=True,
    install_requires=requires,
    license='LGPL',
    zip_safe=False,
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',

    ),
)