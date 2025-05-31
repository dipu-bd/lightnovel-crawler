#!/usr/bin/env sh

VERSION=$(head -n 1 ./lncrawl/VERSION)

PY="python3"
PIP="$PY -m pip --disable-pip-version-check"

rm -rf venv build dist *.egg-info

$PY -m venv venv
. venv/bin/activate

$PIP install -U pip wheel setuptools
$PIP install -r requirements-dev.txt
$PIP install -r requirements-app.txt

$PY setup.py clean bdist_wheel package

deactivate
rm -rf venv build *.egg-info

# FINISHED
