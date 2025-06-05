@ECHO OFF 

SET /P VERSION=<lncrawl\VERSION

SET PY=python
SET PIP=%PY% -m pip --disable-pip-version-check

RD /S /Q "dist" ".venv" "build" "lightnovel_crawler.egg-info" &

%PY% -m venv .venv
CALL .venv\Scripts\activate.bat

%PIP% install -U pip
%PIP% install -r requirements.txt

%PY% -m build -w
%PY% setup_pyi.py

CALL venv\Scripts\deactivate.bat
RD /S /Q ".venv" "build" "lightnovel_crawler.egg-info" &

ECHO ON
