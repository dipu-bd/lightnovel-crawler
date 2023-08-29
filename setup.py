#!/usr/bin/env python
import os
import sys
from glob import glob

if sys.version_info[:2] < (3, 8):
    raise RuntimeError("Lightnovel crawler only supports Python 3.8 and later.")

try:
    from setuptools import config, setup
except ImportError:
    print("Run `pip install setuptools`")
    exit(1)


def parse_requirements(filename):
    with open(filename, "r", encoding="utf8") as f:
        requirements = f.read().strip().split("\n")
        requirements = [
            r.strip() for r in requirements if r.strip() and not r.startswith("#")
        ]
        return requirements


def is_ignored(fname: str):
    try:
        status = os.popen(f"git check-ignore {fname}").read()
        return bool(status.strip())
    except Exception:
        return False


run_pyi = "package" in sys.argv
if run_pyi:
    sys.argv.remove("package")

if len(sys.argv) == 1:
    sys.argv += ["build"]

lncrawl_files = []
lncrawl_packages = ["lncrawl"]
for fname in glob("lncrawl/**/*", recursive=True):
    if os.path.isdir(fname) and not is_ignored(fname):
        lncrawl_packages.append(".".join(fname.split(os.sep)))
    if os.path.isfile(fname) and not is_ignored(fname):
        lncrawl_files.append("/".join(fname.split(os.sep)[1:]))

sources_files = []
sources_packages = ["sources"]
for fname in glob("sources/**/*", recursive=True):
    if os.path.isdir(fname) and not is_ignored(fname):
        sources_packages.append(".".join(fname.split(os.sep)))
    if os.path.isfile(fname) and not is_ignored(fname):
        sources_files.append("/".join(fname.split(os.sep)[1:]))

config.read_configuration("setup.cfg")

setup(
    install_requires=parse_requirements("requirements-app.txt"),
    packages=lncrawl_packages + sources_packages,
    package_data={
        "lncrawl": lncrawl_files,
        "sources": sources_files,
    },
)

if run_pyi:
    from setup_pyi import package

    package()
