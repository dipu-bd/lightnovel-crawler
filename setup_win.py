#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shlex
import shutil
import sys

from PyInstaller import __main__ as pyi
from setuptools.config import read_configuration

dir_name = os.path.abspath(os.path.dirname(__file__))
output = os.path.join(dir_name, 'windows')


def setup_command():
    cur_dir = '/'.join(dir_name.split(os.sep))

    command = 'pyinstaller -y '
    command += '--clean '
    command += '-F '  # onefile
    command += '-n "lncrawl" '
    command += '-i "%s/res/lncrawl.ico" ' % cur_dir

    config = read_configuration('setup.cfg')
    for k, paths in config['options']['.package_data'].items():
        for v in paths:
            src = os.path.normpath('/'.join([cur_dir, k, v]))
            src = '/'.join(src.split(os.sep))
            dst = os.path.normpath('/'.join([k, v]))
            dst = os.path.dirname(dst)
            dst = '/'.join(dst.split(os.sep))
            dst = (dst + '/') if dst else '.'
            command += '--add-data "%s";"%s" ' % (src, dst)
        # end for
    # end for

    command += '"%s/__main__.py" ' % cur_dir

    print(command)
    print()

    extra = ['--distpath', os.path.join(dir_name, 'dist')]
    extra += ['--workpath', os.path.join(output, 'build')]
    extra += ['--specpath', output]

    sys.argv = shlex.split(command) + extra
# end def


def main():
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)
    setup_command()
    pyi.run()
    shutil.rmtree(output, ignore_errors=True)
# end def


if __name__ == '__main__':
    main()
# end if
