#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To prompt if login requires
"""
from PyInquirer import prompt

def login(app):
    answer = prompt([
        {
            'type': 'confirm',
            'name': 'login',
            'message': 'Do you want to log in?',
            'default': False
        },
    ])
    if answer['login']:
        answer = prompt([
            {
                'type': 'input',
                'name': 'email',
                'message': 'Email:',
                'validate': lambda val: 'Email address should be not be empty'
                if len(val) == 0 else True,
            },
            {
                'type': 'password',
                'name': 'password',
                'message': 'Password:',
                'validate': lambda val: 'Password should be not be empty'
                if len(val) == 0 else True,
            },
        ])
        app.crawler.login(answer['email'], answer['password'])
    # end if
# end def
