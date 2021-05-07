# -*- coding: utf-8 -*-
from typing import Optional, Tuple
from questionary import prompt
from ...core.arguments import get_args


def get_login_info(self) -> Optional[Tuple[str, str]]:
    '''Returns the (email, password) pair for login'''
    args = get_args()

    if args.login:
        return args.login
    # end if

    if args.suppress:
        return None
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
                'message': 'User/Email:',
                'validate': lambda a: True if a else 'User/Email should be not be empty'
            },
            {
                'type': 'password',
                'name': 'password',
                'message': 'Password:',
                'validate': lambda a: True if a else 'Password should be not be empty'
            },
        ])
        return answer['email'], answer['password']
    # end if

    return None
# end if
