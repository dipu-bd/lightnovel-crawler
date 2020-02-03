# -*- coding: utf-8 -*-
import re

from PyInquirer import prompt

from ...core import display
from ...core.arguments import get_args
from ...sources import rejected_sources


def get_novel_url(self):
    '''Returns a novel page url or a query'''
    args = get_args()
    if args.query and len(args.query) > 1:
        return args.query
    # end if

    url = args.novel_page
    if url:
        if re.match(r'^https?://.+\..+$', url):
            return url
        else:
            raise Exception('Invalid URL of novel page')
        # end if
    # end if

    try:
        if args.suppress:
            raise Exception()
        # end if

        answer = prompt([
            {
                'type': 'input',
                'name': 'novel',
                'message': 'Enter novel page url or query novel:',
                'validate': lambda val: 'Input should not be empty'
                if len(val) == 0 else True,
            },
        ])
        return answer['novel'].strip()
    except Exception:
        raise Exception('Novel page url or query was not given')
    # end try
# end def


def get_crawlers_to_search(self):
    '''Returns user choice to search the choosen sites for a novel'''
    links = self.app.crawler_links
    if not links:
        return None
    # end if

    args = get_args()
    if args.suppress or not args.sources:
        return links
    # end if

    answer = prompt([
        {
            'type': 'checkbox',
            'name': 'sites',
            'message': 'Where to search?',
            'choices': [{'name': x} for x in sorted(links)],
        }
    ])

    selected = answer['sites']
    return selected if len(selected) > 0 else links
# end def


def choose_a_novel(self):
    '''Choose a single novel url from the search result'''
    args = get_args()

    # Choose a novel title
    choices = self.app.search_results
    selected_choice = self.app.search_results[0]
    if len(choices) > 1 and not args.suppress:
        answer = prompt([
            {
                'type': 'list',
                'name': 'novel',
                'message': 'Which one is your novel?',
                'choices': display.format_novel_choices(choices),
            }
        ])

        index = int(answer['novel'].split('.')[0])
        selected_choice = self.app.search_results[index - 1]
    # end if

    # Choose the novel source
    novels = selected_choice['novels']
    selected_novel = novels[0]
    if len(novels) > 1 and not args.suppress:
        answer = prompt([
            {
                'type': 'list',
                'name': 'novel',
                'message': 'Choose a source to download?',
                'choices': ['0. Back'] + display.format_source_choices(novels),
            }
        ])

        index = int(answer['novel'].split('.')[0])
        if index == 0:
            return self.choose_a_novel()
        # end if
        selected_novel = novels[index - 1]
    # end if

    return selected_novel['url']
# end def
