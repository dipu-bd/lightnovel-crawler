#!/usr/bin/env sh

VERSION=$(head -n 1 ./lncrawl/VERSION)

rm -rf .venv build dist *.egg-info

python3 -m venv .venv
PY=".venv/bin/python"
PIP=".venv/bin/pip --disable-pip-version-check"

$PIP install -U pip
$PIP install -r requirements.txt

$PY -m build -w
$PY setup_pyi.py

deactivate
rm -rf .venv build *.egg-info

# FINISHED
