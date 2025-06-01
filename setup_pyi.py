#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

from PyInstaller import __main__ as pyi

ROOT = Path(__file__).parent
site_packages = list(ROOT.glob(".venv/**/site-packages"))[0]


def build_command():
    command = [
        ROOT / "lncrawl" / "__main__.py",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--name",
        "lncrawl",
        "--icon",
        ROOT / "res" / "lncrawl.ico",
        "--distpath",
        ROOT / "dist",
        "--specpath",
        ROOT / "windows",
        "--workpath",
        ROOT / "windows" / "build",
    ]
    command += gather_data_files()
    command += gather_hidden_imports()
    command += gather_excluded_modules()

    return [str(x) for x in command]


def gather_data_files():
    file_map = {
        ROOT / "lncrawl": "lncrawl",
        ROOT / "sources": "sources",
        site_packages / "cloudscraper": "cloudscraper",
        site_packages / "wcwidth/version.json": "wcwidth",
        site_packages / "text_unidecode/data.bin": "text_unidecode",
    }

    return [
        c for src, dst in file_map.items()
        if src.exists()
        for c in ["--add-data", src.as_posix() + os.pathsep + dst]
    ]


def gather_hidden_imports():
    module_list = []

    for f in (ROOT / "sources").glob("**/*.py"):
        rel_path = str(f.relative_to(ROOT / "sources"))
        if all(x[0].isalnum() for x in rel_path.split(os.sep)):
            module_list.append("sources." + rel_path[:-3].replace(os.sep, "."))

    return [
        c for p in module_list
        for c in ["--hidden-import", p]
    ]


def gather_excluded_modules():
    module_list = [
        'pip',
        'wheel',
        'altgraph',
        'macholib',
        'pyinstaller',
        'pkg_resources',
        'pyinstaller-hooks-contrib',
    ]

    return [
        c for p in module_list
        for c in ["--exclude-module", p]
    ]


def package():
    command = build_command()
    print('  '.join(command))
    print('-' * 40)

    output = str(ROOT / "windows")
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)

    pyi.run(command)
    shutil.rmtree(output, ignore_errors=True)


if __name__ == "__main__":
    package()
