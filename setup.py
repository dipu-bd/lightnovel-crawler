#!/usr/bin/env python
import sys

if sys.version_info[:2] < (3, 5):
    raise RuntimeError(
        'Lightnovel crawler only supports Python 3.5 and later.')
else:
    from setuptools import config, setup

    config.read_configuration('setup.cfg')
    setup()
# end if
