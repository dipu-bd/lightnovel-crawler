#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

cur_dir = os.path.dirname(__file__)
ver_file = os.path.join(cur_dir, '..', '..', 'VERSION')
with open(ver_file, 'r') as f:
    version = f.read().strip()
# end with


def get_value():
    return version
# end def
