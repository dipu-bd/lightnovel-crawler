#!/bin/bash

VERSION=$(head -n 1 src/VERSION)

rm -rf venv build dist *.egg-info __pycache__

python3 -m venv venv
. venv/bin/activate

python -m pip install -U pip==19.2.1

python3 -m pip install wheel
python3 -m pip install PyInstaller
python3 -m pip install -r requirements.txt

python3 setup.py bdist_wheel sdist package

deactivate
rm -rf venv build *.egg-info __pycache__

python3 -m pip install twine
twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"

# END
