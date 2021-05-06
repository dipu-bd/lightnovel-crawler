#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import shlex
import shutil
import site
import sys
from pathlib import Path

from PyInstaller import __main__ as pyi

ROOT = Path(__file__).parent
unix_root = '/'.join(str(ROOT).split(os.sep))
unix_site_packages = '/'.join(site.USER_SITE.split(os.sep))


def package():
    output = str(ROOT / 'windows')
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)
    setup_command()
    pyi.run()
    shutil.rmtree(output, ignore_errors=True)
# end def


def setup_command():
    command = 'pyinstaller '
    command += '--onefile '  # onefile
    command += '--clean '
    command += '--noconfirm '
    command += '--name "lncrawl" '
    command += '--icon "%s/res/lncrawl.ico" ' % unix_root
    command += '--distpath "%s" ' % str(ROOT / 'dist')
    command += '--specpath "%s" ' % str(ROOT / 'windows')
    command += '--workpath "%s" ' % str(ROOT / 'windows' / 'build')

    command += gather_data_files()
    command += gather_hidden_imports()
    command += '"%s/__main__.py" ' % unix_root

    print(command)
    print()

    sys.argv = shlex.split(command)
# end def


def gather_data_files():
    command = ''

    # add data files of this project
    for f in (ROOT / 'lncrawl').glob('**/*.*'):
        src = str(f)
        src = '/'.join(src.split(os.sep))
        dst = str(f.parent.relative_to(ROOT))
        dst = '/'.join(dst.split(os.sep))
        command += '--add-data "%s%s%s" ' % (src, os.pathsep, dst)
    # end for
    command += '--add-data "%s/lncrawl/VERSION%slncrawl" ' % (unix_root, os.pathsep)

    # add data files of other dependencies
    command += '--add-data "%s/cairosvg/VERSION%s." ' % (unix_site_packages, os.pathsep)
    command += '--add-data "%s/cairocffi/VERSION%scairocffi" ' % (unix_site_packages, os.pathsep)
    # command += '--add-data "%s/tinycss2/VERSION%stinycss2" ' % (unix_site_packages, os.pathsep)
    command += '--add-data "%s/text_unidecode/data.bin%stext_unidecode" ' % (unix_site_packages, os.pathsep)
    command += '--add-data "%s/cloudscraper%scloudscraper" ' % (unix_site_packages, os.pathsep)
    command += '--add-data "%s/wcwidth/version.json%swcwidth" ' % (unix_site_packages, os.pathsep)

    return command
# end def


def gather_hidden_imports():
    command = ''

    # add hidden imports of this project
    for f in (ROOT / 'lncrawl' / 'sources').glob('*.py'):
        if os.path.isfile(f) and re.match(r'^([^_.][^.]+).py$', f.name):
            module_name = f.name[:-3]
            command += '--hidden-import "lncrawl.sources.%s" ' % module_name
        # end if
    # end for
    command += '--hidden-import "pkg_resources.py2_warn" '

    return command
# end def


if __name__ == '__main__':
    package()
# end if
