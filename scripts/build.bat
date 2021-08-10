@ECHO OFF 

SET /P VERSION=<lncrawl\VERSION

SET PY=python
SET PIP=%PY% -m pip --disable-pip-version-check

RD /S /Q "dist" "venv" "build" "lightnovel_crawler.egg-info" &

%PY% -m venv venv
CALL venv\Scripts\activate.bat

%PIP% install -U pip wheel setuptools
%PIP% install -r requirements-dev.txt
%PIP% install -r requirements-app.txt

%PY% setup.py clean bdist_wheel package

CALL venv\Scripts\deactivate.bat
RD /S /Q "venv" "build" "lightnovel_crawler.egg-info" &

ECHO ON
