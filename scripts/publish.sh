#!/bin/bash

VERSION=$(head -n 1 lncrawl/VERSION)

PY="python3"
PIP="$PY -m pip --disable-pip-version-check"

# . scripts/build.sh

$PIP install twine
$PY -m twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"

# FINISHED
