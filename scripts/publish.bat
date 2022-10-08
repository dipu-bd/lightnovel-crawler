@ECHO OFF

SET /P VERSION=<lncrawl\VERSION

SET PY=python
SET PIP=%PY% -m pip --disable-pip-version-check

REM CALL scripts\build.bat

%PIP% install twine
%PY% -m twine upload "dist\lightnovel_crawler-%VERSION%-py3-none-any.whl"

ECHO ON
