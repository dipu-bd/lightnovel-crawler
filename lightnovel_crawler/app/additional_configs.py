#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To prompt for additional configs
"""
from PyInquirer import prompt

def additional_configs(app):
    answer = prompt([
        {
            'type': 'confirm',
            'name': 'volume',
            'message': 'Generate separate files for each volumes?',
            'default': False,
        },
    ])
    app.pack_by_volume = answer['volume']
# end def
