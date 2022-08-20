@ECHO OFF

SET /P VERSION=<lncrawl\VERSION

git pull --rebase

git push --delete origin "v%VERSION%"
git tag -d "v%VERSION%"
git tag "v%VERSION%"
git push --tags

ECHO ON
