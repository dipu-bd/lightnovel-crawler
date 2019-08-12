#!/bin/bash

VERSION=$(head -n 1 VERSION)

rm -rf venv build dist *.egg-info __pycache__

python3 -m venv venv
. venv/bin/activate

python -m pip install --upgrade pip

python3 -m pip install wheel
python3 -m pip install PyInstaller
python3 -m pip install -r requirements.txt

python3 setup.py bdist_wheel sdist package

python3 -m pip install twine
twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"

git tag -d "v$VERSION"
git tag -a "v$VERSION" -m "Version $VERSION"

deactivate

rm -rf venv build *.egg-info __pycache__
