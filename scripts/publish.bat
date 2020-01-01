@ECHO OFF 

SET /P VERSION=<src\VERSION

CALL scripts\build.bat

%PIP% install twine
twine upload "dist\lightnovel_crawler-%VERSION%-py3-none-any.whl"

ECHO ON
