#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""
from PyInquirer import prompt
from .program import Program
from ..utils.crawler import Crawler


def check(crawler):
    return crawler.__bases__.count(Crawler) == 1
# end for

def start_app(choice_list):
    print('\n⮕ Press \33[95mCtrl + C\33[0m to exit\n')

    answer = prompt([
        {
            'type': 'list',
            'name': 'source',
            'message': 'Where is the novel from?',
            'choices': [
                {
                    'name': key,
                    'disabled': False if check(choice_list[key]) \
                        else 'Not yet implemented',
                } for key in choice_list
            ],
        },
    ])

    crawler = choice_list[answer['source']]
    Program().run(crawler())

    print('-' * 80, end='\n\n')
    print('Bye... Come back soon!')
# end def
