# -*- coding: utf-8 -*-
'''
Source: https://stackoverflow.com/a/44820157/1583052
'''
import sys
import os

STDOUT_ENCODING = str(sys.stdout.encoding)
try:
    PYTHONIOENCODING = str(os.environ["PYTHONIOENCODING"])
except:
    PYTHONIOENCODING = False

# Remark: In case the stdout gets modified, it will only append all information
# that has been written into the pipe until that very moment.
if sys.stdout.isatty() is False:
    print("Program is running in piping mode. (sys.stdout.isatty() is " + str(sys.stdout.isatty()) + ".)")
    if PYTHONIOENCODING is not False:
        print("PYTHONIOENCODING is set to a value. ('" + str(PYTHONIOENCODING) + "')")
        if str(sys.stdout.encoding) != str(PYTHONIOENCODING):
            print("PYTHONIOENCODING is differing from stdout encoding. ('" + str(PYTHONIOENCODING) + "' != '" + STDOUT_ENCODING +
                  "'). This should normally not happen unless the PyInstaller setup is still broken. Setting hard utf-8 workaround.")
            sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)
            print("PYTHONIOENCODING was differing from stdout encoding. ('" + str(PYTHONIOENCODING) + "' != '" + STDOUT_ENCODING +
                  "'). This should normally not happen unless PyInstaller is still broken. Setting hard utf-8 workaround. New encoding: '" + str(PYTHONIOENCODING) + "'.", "D")
    else:
        print("PYTHONIOENCODING is set False. ('" + str(PYTHONIOENCODING) + "'). - Nothing to do.")
