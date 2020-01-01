# -*- coding: utf-8 -*-
from PyInquirer import prompt
from ...core.arguments import get_args


def get_login_info(self):
    '''Returns the (email, password) pair for login'''
    args = get_args()

    if args.login:
        return args.login
    # end if

    if args.suppress:
        return False
    # end if

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
                'message': 'Username/Email:',
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
        return answer['email'], answer['password']
    # end if

    return None
# end if
