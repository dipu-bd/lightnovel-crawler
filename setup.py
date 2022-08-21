#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from glob import glob
from pathlib import Path
from fnmatch import fnmatch

if sys.version_info[:2] < (3, 6):
    raise RuntimeError(
        'Lightnovel crawler only supports Python 3.6 and later.')

try:
    import setuptools
    from setuptools import config, setup
finally:
    pass
 

run_pyi = 'package' in sys.argv
if run_pyi:
    sys.argv.remove('package')
# end if
if len(sys.argv) == 1:
    sys.argv += ['build']
# end if


def parse_requirements(filename):
    with open(filename, 'r', encoding='utf8') as f:
        requirements = f.read().strip().split('\n')
        requirements = [
            r.strip() for r in requirements
            if r.strip() and not r.startswith('#')
        ]
        return requirements
# end def


config.read_configuration('setup.cfg')

packages = setuptools.find_packages()
sources_packages = [
    ('lncrawl/' + p.as_posix()).replace('/', '.')
    for p in Path('sources').glob('**')
]

files = Path("lncrawl").iterdir()
with open(".gitignore") as gitignore_file:
    gitignore = [line for line in gitignore_file.read().splitlines() if line]
lncrawl_files = [
    '/'.join(fname.split(os.sep)[1:])
    for fname in glob('lncrawl/**/*', recursive=True) 
    if os.path.isfile(fname) and not any(fnmatch(fname, ignore) for ignore in gitignore)
]

setup(
    packages=packages + sources_packages,
    package_dir = {
        'lncrawl.sources': 'sources'
    },
    package_data = {
        'lncrawl': lncrawl_files,
        'lncrawl.sources': ['*.*'],
    },
    install_requires=parse_requirements('requirements-app.txt'),
)

if run_pyi:
    from setup_pyi import package
    package()
# end if
