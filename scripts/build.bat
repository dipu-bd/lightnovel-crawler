@ECHO OFF 

SET /P VERSION=<src\VERSION

SET PY=python
SET PIP=%PY% -m pip --disable-pip-version-check

RD /S /Q "dist" "venv" "build" "lightnovel_crawler.egg-info" &

%PY% -m venv venv
CALL venv\Scripts\activate.bat

%PIP% install -U pip==20.0.2
%PIP% install -U wheel setuptools

%PIP% install PyInstaller cairosvg
%PIP% install -r requirements.txt

%PY% setup.py clean bdist_wheel sdist package

CALL venv\Scripts\deactivate.bat
RD /S /Q "venv" "build" "lightnovel_crawler.egg-info" &

ECHO ON
