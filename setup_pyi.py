#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import re
import shlex
import shutil
import sys
from pathlib import Path

from PyInstaller import __main__ as pyi
from setuptools.config import read_configuration

ROOT = Path(__file__).parent
unix_root = '/'.join(str(ROOT).split(os.sep))


def package():
    output = str(ROOT / 'windows')
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)
    setup_command()
    pyi.run()
    shutil.rmtree(output, ignore_errors=True)
# end def


def setup_command():
    command = 'pyinstaller -y '
    command += '--clean '
    command += '-F '  # onefile
    command += '-n "lncrawl" '
    command += '-i "%s/res/lncrawl.ico" ' % unix_root
    command += gather_data_files()
    command += '"%s/__main__.py" ' % unix_root

    print(command)
    print()

    extra = ['--distpath', str(ROOT / 'dist')]
    extra += ['--specpath', str(ROOT / 'windows')]
    extra += ['--workpath', str(ROOT / 'windows' / 'build')]

    sys.argv = shlex.split(command) + extra
# end def


def gather_data_files():
    command = ''

    # add data files of my project
    py_matcher = re.compile(r'\.pyc?$', flags=re.I)
    for f in (ROOT / 'src' / 'assets').glob('**/*.*'):
        src = str(f)
        if py_matcher.search(src):
            continue
        # end if
        src = '/'.join(src.split(os.sep))
        dst = str(f.parent.relative_to(ROOT))
        dst = '/'.join(dst.split(os.sep))
        command += '--add-data "%s%s%s" ' % (src, os.pathsep, dst)
    # end for
    command += '--add-data "%s/src/VERSION%ssrc" ' % (unix_root, os.pathsep)

    # add data files of other dependencies
    site_packages = list(ROOT.glob('venv/**/site-packages'))[0]
    site_packages = '/'.join(str(site_packages).split(os.sep))
    command += '--add-data "%s/cairosvg/VERSION%s." ' % (
        site_packages, os.pathsep)
    command += '--add-data "%s/cairocffi/VERSION%scairocffi" ' % (
        site_packages, os.pathsep)
    command += '--add-data "%s/tinycss2/VERSION%stinycss2" ' % (
        site_packages, os.pathsep)

    return command
# end def


if __name__ == '__main__':
    package()
# end if
