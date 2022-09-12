#!/bin/bash

VERSION=$(head -n 1 lncrawl/VERSION)

git pull --rebase

git tag "v$VERSION"
git push --tags
