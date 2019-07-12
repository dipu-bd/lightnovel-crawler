#!/bin/bash

VERSION=$(head -n 1 VERSION)

rm -rf build dist *.egg-info __pycache__

python3 setup.py bdist_wheel sdist

twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"

git tag -a "v$VERSION" -m "Version $VERSION"
