@ECHO OFF 

SET /P VERSION=<src\VERSION

SET PY=python
SET PIP=%PY% -m pip --disable-pip-version-check

RD /S /Q "dist" "venv" "build" "lightnovel_crawler.egg-info" &

%PY% -m venv venv
CALL venv\Scripts\activate.bat

%PIP% install -U pip==19.2.1

%PIP% install wheel
%PIP% install PyInstaller
%PIP% install -r requirements.txt

%PY% setup.py clean bdist_wheel sdist package

CALL venv\Scripts\deactivate.bat
RD /S /Q "venv" "build" "lightnovel_crawler.egg-info" &

ECHO ON
