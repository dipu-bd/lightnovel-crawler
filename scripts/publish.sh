#!/bin/bash

VERSION=$(head -n 1 src/VERSION)

# . scripts/build.sh

$PIP install twine
twine upload "dist/lightnovel_crawler-$VERSION-py3-none-any.whl"

# FINISHED
