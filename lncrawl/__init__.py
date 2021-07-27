#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
# end try


def main():
    from .core import start_app
    start_app()
# end def

if __name__ == "__main__":
     main()
