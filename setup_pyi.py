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

dir_name = os.path.abspath(os.path.dirname(__file__))
output = os.path.join(dir_name, 'windows')


def setup_command():
    cur_dir = '/'.join(dir_name.split(os.sep))

    command = 'pyinstaller -y '
    command += '--clean '
    # command += '-F '  # onefile
    command += '-n "lncrawl" '
    command += '-i "%s/res/lncrawl.ico" ' % cur_dir
    command += '--version-file "%s/VERSION" ' % cur_dir

    sep = ';' if platform.system() == 'Windows' else ':'
    py_matcher = re.compile(r'\.pyc?$', flags=re.I)
    assets_dir = Path(os.path.join(cur_dir, 'src', 'assets'))
    for f in assets_dir.glob('**/*.*'):
        src = str(f)
        if py_matcher.search(src):
            continue
        # end if
        src = '/'.join(src.split(os.sep))
        dst = str(f.parent.relative_to(cur_dir))
        dst = '/'.join(dst.split(os.sep))
        command += '--add-data "%s%s%s" ' % (src, sep, dst)
    # end for
    command += '--add-data "%s/VERSION%s." ' % (cur_dir, sep)

    command += '"%s/__main__.py" ' % cur_dir

    print(command)
    print()

    extra = ['--distpath', os.path.join(dir_name, 'dist')]
    extra += ['--workpath', os.path.join(output, 'build')]
    extra += ['--specpath', output]

    sys.argv = shlex.split(command) + extra
# end def


def package():
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)
    setup_command()
    pyi.run()
    shutil.rmtree(output, ignore_errors=True)
# end def


if __name__ == '__main__':
    package()
# end if
