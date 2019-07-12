#!/bin/bash

rm -rf venv build dist

python3 -m venv venv
. venv/bin/activate

python3 -m pip install wheel
python3 -m pip install pyinstaller

python3 -m pip install -r requirements.txt

python3 setup_pyi.py

deactivate
rm -rf venv build
