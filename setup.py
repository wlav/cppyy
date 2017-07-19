#!/usr/bin/env python

import os, glob
from setuptools import setup, find_packages, Extension
from codecs import open


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

try:
    import __pypy__
    requirements = ['PyPy-cppyy-backend']
except ImportError:
    requirements = ['CPyCppyy']


setup(
    name='cppyy',
    version='0.1.0',
    description='Cling-based Python-C++ bindings',
    long_description=long_description,

    url='http://cppyy.readthedocs.io/en/latest',

    # Author details
    author='Wim Lavrijsen',
    author_email='WLavrijsen@lbl.gov',

    license='LBNL BSD',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'Topic :: Software Development',
        'Topic :: Software Development :: Interpreters',

        #'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: C',
        'Programming Language :: C++',

        'Natural Language :: English'
    ],

    install_requires=requirements,

    keywords='C++ bindings',

)

