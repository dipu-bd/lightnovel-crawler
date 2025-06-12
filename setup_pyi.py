#!/usr/bin/env python
import os
import shutil
import sys
from pathlib import Path

if sys.version_info[:2] < (3, 8):
    raise RuntimeError("This app only supports Python 3.8 and later.")

ROOT = Path(__file__).resolve().parent

AVAILABLE_SITE_PACKAGES = list(ROOT.glob(".venv/**/site-packages"))
if not AVAILABLE_SITE_PACKAGES:
    raise RuntimeError("No site-packages found in .venv")

SITE_PACKAGES = AVAILABLE_SITE_PACKAGES[0]
DIST_DIR = ROOT / "dist"
SPEC_DIR = ROOT / "windows"
BUILD_DIR = SPEC_DIR / "build"


def build_command():
    command = [
        str(ROOT / "lncrawl" / "__main__.py"),
        "--onefile",
        "--clean",
        "--noconfirm",
        "--name=lncrawl",
        f"--icon={ROOT / 'res' / 'lncrawl.ico'}",
        f"--distpath={DIST_DIR}",
        f"--specpath={SPEC_DIR}",
        f"--workpath={BUILD_DIR}",
    ]
    command += gather_data_files()
    command += gather_hidden_imports()
    command += gather_excluded_modules()
    return command


def gather_data_files():
    file_map = {
        ROOT / "lncrawl": "lncrawl",
        ROOT / "sources": "sources",
        SITE_PACKAGES / "cloudscraper": "cloudscraper",
        SITE_PACKAGES / "wcwidth" / "version.json": "wcwidth",
        SITE_PACKAGES / "text_unidecode" / "data.bin": "text_unidecode",
    }

    results = []
    for src, dst in file_map.items():
        if src.exists():
            results.extend([
                '--add-data', f'{src.as_posix()}:{dst}'
            ])
    return results


def gather_hidden_imports():
    hidden = [
        'passlib.handlers.argon2',
    ]

    for py_file in (ROOT / "sources").rglob("*.py"):
        rel_path = str(py_file.relative_to(ROOT / "sources"))
        if all(x[0].isalnum() for x in rel_path.split(os.sep)):
            module = "sources." + rel_path[:-3].replace(os.sep, ".")
            hidden.append(module)

    return [
        f"--hidden-import={module}"
        for module in hidden
    ]


def gather_excluded_modules():
    exclude = [
        'pip',
        'wheel',
        'altgraph',
        'macholib',
        'pyinstaller',
        'pkg_resources',
        'pyinstaller-hooks-contrib',
    ]
    return [
        flag for mod in exclude
        for flag in ["--exclude-module", mod]
    ]


def package():
    command = build_command()

    print("🔧 Running PyInstaller:")
    print(" ".join(command))
    print("-" * 60)

    # Cleanup and prepare build directory
    shutil.rmtree(SPEC_DIR, ignore_errors=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    # Run PyInstaller
    from PyInstaller import __main__ as pyi  # type:ignore
    pyi.run(command)

    # Cleanup temp build dir
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

    # Final output confirmation
    OUTPUT_EXE = DIST_DIR / 'lncrawl.exe'
    OUTPUT_POSIX = DIST_DIR / 'lncrawl'
    if OUTPUT_EXE.is_file():
        print(f"✅ Executable created: {OUTPUT_EXE}")
    elif OUTPUT_POSIX.is_file():
        print(f"✅ Executable created: {OUTPUT_POSIX}")
    else:
        print("❌ Build failed: Output not found.")


if __name__ == "__main__":
    package()
