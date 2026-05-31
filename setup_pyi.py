#!/usr/bin/env python
import os
from pathlib import Path
import shutil
import sys

if sys.version_info[:2] < (3, 9):
    raise RuntimeError("This app only supports Python 3.9 and later.")

IS_WINDOWS = sys.platform == "win32"

ROOT = Path(__file__).resolve().parent

# Determine venv directory: use VIRTUAL_ENV if set, otherwise detect based on OS
VENV_DIR = os.getenv("VIRTUAL_ENV")
if VENV_DIR:
    VENV_DIR = Path(VENV_DIR).relative_to(ROOT).as_posix()
elif (ROOT / ".venv-win").exists():
    VENV_DIR = ".venv-win"
elif (ROOT / ".venv-posix").exists():
    VENV_DIR = ".venv-posix"
else:
    VENV_DIR = ".venv"
AVAILABLE_SITE_PACKAGES = list(ROOT.glob(f"{VENV_DIR}/**/site-packages"))
if not AVAILABLE_SITE_PACKAGES:
    raise RuntimeError(f"No site-packages found in {VENV_DIR}")

SITE_PACKAGES = AVAILABLE_SITE_PACKAGES[0]
DIST_DIR = ROOT / "dist"
SPEC_DIR = ROOT / "windows"
BUILD_DIR = SPEC_DIR / "build"


def build_command():
    command = [
        str(ROOT / "lncrawl" / "__main__.py"),
        "--onedir" if IS_WINDOWS else "--onefile",
        "--clean",
        "--noconfirm",
        "--name=lncrawl",
        f"--icon={ROOT / 'res' / 'lncrawl.ico'}",
        "--collect-all=pylsp",
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
        ROOT / "pyproject.toml": ".",
        ROOT / "lncrawl": "lncrawl",
        ROOT / "sources": "sources",
        SITE_PACKAGES / "wcwidth" / "version.json": "wcwidth",
        SITE_PACKAGES / "text_unidecode" / "data.bin": "text_unidecode",
    }

    results = []
    for src, dst in file_map.items():
        if src.exists():
            results.extend(["--add-data", f"{src.as_posix()}:{dst}"])
    return results


def gather_hidden_imports():
    hidden = [
        "passlib.handlers.argon2",
    ]

    for py_file in (ROOT / "sources").rglob("*.py"):
        rel_path = str(py_file.relative_to(ROOT / "sources"))
        if all(x[0].isalnum() for x in rel_path.split(os.sep)):
            module = "sources." + rel_path[:-3].replace(os.sep, ".")
            hidden.append(module)

    return [f"--hidden-import={module}" for module in hidden]


def gather_excluded_modules():
    exclude = [
        "pip",
        "wheel",
        "ujson",
        "altgraph",
        "macholib",
        "pyinstaller",
        "pkg_resources",
        "pyinstaller-hooks-contrib",
    ]
    return [flag for mod in exclude for flag in ["--exclude-module", mod]]


def package():
    command = build_command()

    print("🔧 Running PyInstaller:")
    print(" ".join(command))
    print("-" * 60)

    # Cleanup only build artifacts inside the spec dir, not the whole directory
    # (installer.iss and other files in windows/ must be preserved)
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    for spec_file in SPEC_DIR.glob("*.spec"):
        spec_file.unlink(missing_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    # Run PyInstaller
    from PyInstaller import __main__ as pyi  # type: ignore

    pyi.run(command)

    # Cleanup temp build dir
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

    # Final output confirmation
    OUTPUT_WIN = DIST_DIR / "lncrawl" / "lncrawl.exe"  # onedir (Windows)
    OUTPUT_POSIX = DIST_DIR / "lncrawl"  # onefile (Mac/Linux)
    if OUTPUT_WIN.is_file():
        print(f"✅ Executable created: {OUTPUT_WIN}")
    elif OUTPUT_POSIX.is_file():
        print(f"✅ Executable created: {OUTPUT_POSIX}")
    else:
        print("❌ Build failed: Output not found.")


if __name__ == "__main__":
    package()
