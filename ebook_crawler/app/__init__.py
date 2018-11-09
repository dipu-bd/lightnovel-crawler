#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
from .program import Program

def run_app(crawler):
    if crawler:
        Program().run(crawler)
    # end if
# end def
