#!/usr/bin/env python3

from contextlib import suppress
import os
import sys

# For encoding
with suppress(Exception):
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")

# For executable bundles
is_frozen = bool(__package__ and getattr(sys, "frozen", False))
if is_frozen:
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

    with suppress(Exception):
        import multiprocessing

        multiprocessing.freeze_support()

# Remove colors from terminal (Windows frozen builds and CI environments don't support ANSI)
if os.getenv("CI") or (is_frozen and sys.platform == "win32"):
    os.environ["TERM"] = "dumb"
    os.environ["NO_COLOR"] = "1"


def main():
    if os.environ.get("LNCRAWL_PYLSP") == "1":
        # Start pylsp server
        from pylsp import __main__ as _pylsp_main

        _pylsp_main.main()
    elif is_frozen and len(sys.argv) <= 1:
        # No CLI args: double-click launch — hide the console window then start the GUI.
        # The exe is built as a console subsystem app (so CLI works properly),
        # so we hide the console window here before opening the webview.
        if sys.platform == "win32":
            import ctypes

            ctypes.windll.kernel32.FreeConsole()

        from .server.webview import start

        start()
    else:
        # Start main app
        from .app import app

        app()


if __name__ == "__main__":
    main()
