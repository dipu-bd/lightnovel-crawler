#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import shutil
from pathlib import Path

from PyInstaller import __main__ as pyi

ROOT = Path(__file__).parent
site_packages = list(ROOT.glob('venv/**/site-packages'))[0]


def build_command():
    command = [
        ROOT / 'lncrawl' / '__main__.py',
        '--onefile',
        '--clean',
        '--noconfirm',
        '--name', 'lncrawl',
        '--icon',  ROOT / 'res' / 'lncrawl.ico',
        '--distpath', ROOT / 'dist',
        '--specpath', ROOT / 'windows',
        '--workpath', ROOT / 'windows' / 'build',
    ]
    command += gather_data_files()
    command += gather_hidden_imports()

    return [str(x) for x in command]


def gather_data_files():
    file_map = {
        ROOT / 'lncrawl': 'lncrawl',
        ROOT / 'sources': 'sources',
        site_packages / 'cloudscraper': 'cloudscraper',
        site_packages / 'wcwidth/version.json': 'wcwidth',
        site_packages / 'text_unidecode/data.bin': 'text_unidecode',
    }

    command = []
    for src, dst in file_map.items():
        command += ['--add-data', src.as_posix() + os.pathsep + dst]

    return command


def gather_hidden_imports():
    module_list = [
        'pkg_resources.py2_warn',
    ]

    for f in (ROOT / 'sources').glob('*.py'):
        if f.name[0].isalnum():
            module_list.append('sources.' + f.name[:-3])

    command = []
    for p in module_list:
        command += ['--hidden-import', p]

    return command
# end def


def package():
    output = str(ROOT / 'windows')
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)
    pyi.run(build_command())
    shutil.rmtree(output, ignore_errors=True)
# end def


if __name__ == '__main__':
    package()
# end if
