#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To prompt if login requires
"""
from PyInquirer import prompt

def login(crawler):
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
                'validate': lambda val: True if len(val)
                    else 'Email address should be not be empty'
            },
            {
                'type': 'password',
                'name': 'password',
                'message': 'Password:',
                'validate': lambda val: True if len(val)
                    else 'Password should be not be empty'
            },
        ])
        crawler.login(answer['email'], answer['password'])
    # end if
# end def
