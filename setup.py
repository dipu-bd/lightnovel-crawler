#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import sys
from os import path, getenv
from setuptools import setup, find_packages
from setup_config import *

setup(
    name=package_name,
    version=current_version,
    description=short_description,
    entry_points=entry_points,
    install_requires=install_requires,
    include_package_data=True,
    package_data=package_data,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dipu-bd/lightnovel-crawler',
    author='Sudipto Chandra',
    author_email='dipu.sudipta@gmail.com',
    keywords=package_keywords,
    packages=find_packages(exclude=[
        'contrib',
        'docs',
        'tests',
        'tests.*'
    ]),
    project_urls={
        'Source': 'https://github.com/dipu-bd/lightnovel-crawler/',
        'Bug Reports': 'https://github.com/dipu-bd/lightnovel-crawler/issues',
        # 'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'https://saythanks.io/to/dipu-bd',
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Pick your license as you wish
        'License :: Free For Home Use',

        # Indicate who your project is intended for
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Education',
        'Topic :: Text Processing',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
     
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
    ],
)
