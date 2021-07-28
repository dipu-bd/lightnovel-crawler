@ECHO OFF

SET /P VERSION=<lncrawl\VERSION

@REM git push --delete origin "v%VERSION%"
@REM git tag -d "v%VERSION%"
git tag "v%VERSION%"
git push --tags

ECHO ON
