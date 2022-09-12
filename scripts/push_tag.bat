@ECHO OFF

SET /P VERSION=<lncrawl\VERSION

git pull --rebase

git tag "v%VERSION%"
git push --tags

ECHO ON
