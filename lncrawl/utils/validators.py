#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validators for py inquirer"""
import math
import regex

def validateNumber(val, start, stop):
    try:
        val = int(val)
    except:
        return 'Enter a number'
    # end try
    if math.isfinite(start) and val < start:
        return 'Number should be greater or equal to %d' % start
    elif math.isfinite(stop) and val > stop:
        return 'Number should be lesser or equal to %d' % stop
    else:
        return True
    # end if
# end def
