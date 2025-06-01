#!/usr/bin/env sh

VERSION=$(head -n 1 ./lncrawl/VERSION)

rm -rf .venv build dist *.egg-info

python3 -m venv .venv
PY=".venv/bin/python"
PIP=".venv/bin/pip --disable-pip-version-check"

$PIP install -U pip wheel setuptools
$PIP install -r requirements-dev.txt
$PIP install -r requirements-app.txt

$PY setup.py clean bdist_wheel package

deactivate
rm -rf .venv build *.egg-info

# FINISHED
