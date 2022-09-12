# -*- coding: utf-8 -*-
from prompt_toolkit.styles.style import Style
from questionary import prompt
from questionary.prompts.common import Choice

from ...core.arguments import get_args


def get_range_selection(self, disable_args=False):
    '''
    Returns a choice of how to select the range of chapters to downloads
    '''
    volume_count = len(self.app.crawler.volumes)
    chapter_count = len(self.app.crawler.chapters)
    selections = ['all', 'last', 'first',
                  'page', 'range', 'volumes', 'chapters']

    args = get_args()

    if not disable_args:
        for key in selections:
            if args.__getattribute__(key):
                return key
            # end if
        # end if
    # end if
    
    if args.suppress:
        return selections[0]
    # end if
 
    choices = [
        'Everything! (%d chapters)' % chapter_count,
        'Last 10 chapters',
        'First 10 chapters',
        'Custom range using URL',
        'Custom range using index',
        'Select specific volumes (%d volumes)' % volume_count,
        'Select specific chapters ' + ('(warn: very big list)' if chapter_count > 50 else ''),
    ]
    if chapter_count <= 20:
        choices.pop(1)
        choices.pop(1)
    # end if

    answer = prompt([
        {
            'type': 'list',
            'name': 'choice',
            'message': 'Which chapters to download?',
            'choices': choices,
        },
    ])

    return selections[choices.index(answer['choice'])]
# end def


def get_range_using_urls(self, disable_args=False):
    '''Returns a range of chapters using start and end urls as input'''
    args = get_args()

    if args.page:
        start = self.app.crawler.get_chapter_index_of(args.page[0]) - 1
    else:
        start = -1
    # end if

    if args.page and len(args.page) > 1:
        stop = self.app.crawler.get_chapter_index_of(args.page[1]) - 1
    else:
        stop = -1
    # end if

    if args.suppress and start < 0:
        return (0, len(self.app.crawler.chapters) - 1)
    # end if

    if disable_args or start < 0:
        def _validator(is_optional):
            def _internal_validator(val):
                try:
                    if is_optional and not val:
                        return True
                    if self.app.crawler.get_chapter_index_of(val) > 0:
                        return True
                except Exception:
                    pass
                return 'No such chapter found given the url'
            return _internal_validator
        # end def
        
        answer = prompt([
            {
                'type': 'autocomplete',
                'name': 'start_url',
                'message': 'Enter start url:',
                'choices': [chap['url'] for chap in self.app.crawler.chapters],
                'validate': _validator(False),
            },
            {
                'type': 'autocomplete',
                'name': 'stop_url',
                'message': 'Enter final url (optional):',
                'choices': [chap['url'] for chap in self.app.crawler.chapters],
                'validate': _validator(True),
            },
        ], style=Style([
            ("selected", "fg:#000000 bold"),
            # ("highlighted", "fg:#000000 bold"),
            ("answer", "fg:#f44336 bold"),
            ("text", ""),
        ]))
        start = self.app.crawler.get_chapter_index_of(answer['start_url']) - 1
        stop = self.app.crawler.get_chapter_index_of(answer['stop_url']) - 1
    # end if

    if stop < 0:
        stop = len(self.app.crawler.chapters) - 1
    elif stop < start:
        stop = start
    # end if

    return (start, stop)
# end def


def get_range_using_index(self, disable_args=False):
    '''Returns a range selected using chapter indices'''
    chapter_count = len(self.app.crawler.chapters)

    args = get_args()
    start, stop = args.range or (None, None)

    if args.suppress and not (start and stop):
        return (0, chapter_count - 1)
    # end if

    if disable_args or not start:
        def validator(val):
            try:
                if 1 <= int(val) <= chapter_count:
                    return True
            except Exception:
                pass
            return 'Enter an integer between 1 and %d' % chapter_count
        # end def
        answer = prompt([
            {
                'type': 'input',
                'name': 'start',
                'message': 'Enter start index (1 to %d):' % chapter_count,
                'validate': validator,
                'filter': lambda val: int(val),
            },
            {
                'type': 'input',
                'name': 'stop',
                'message': 'Enter final index (1 to %d):' % chapter_count,
                'validate': validator,
                'filter': lambda val: int(val),
            },
        ])
        start = answer['start'] - 1
        stop = answer['stop'] - 1
    else:
        start = start - 1
        stop = stop - 1
    # end if

    return (start, stop) if start < stop else (stop, start)
# end def


def get_range_from_volumes(self, times=0, disable_args=False):
    '''Returns a range created using volume list'''
    selected = None
    args = get_args()

    if times == 0 and args.volumes:
        selected = [int(x) for x in args.volumes]
    # end if

    if not selected and args.suppress:
        selected = [x['id'] for x in self.app.crawler.volumes]
    # end if

    if disable_args or not selected:
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'volumes',
                'message': 'Choose volumes to download:',
                'choices': [
                    Choice(
                        '%d - %s (Chapter %d-%d) [%d chapters]' % (
                            vol['id'], vol['title'], vol['start_chapter'],
                            vol['final_chapter'], vol['chapter_count']),
                    )
                    for vol in self.app.crawler.volumes
                ],
                'validate': lambda a: True if a else (False, "Select at least one item")
            }
        ])
        selected = [int(val.split(' ')[0]) for val in answer['volumes']]
    # end if

    if times < 3 and len(selected) == 0:
        return self.get_range_from_volumes(times + 1)
    # end if

    return selected
# end def


def get_range_from_chapters(self, times=0, disable_args=False):
    '''Returns a range created using individual chapters'''
    selected = None
    args = get_args()

    if times == 0 and not selected:
        selected = get_args().chapters
    # end if

    if not selected and args.suppress:
        selected = self.app.crawler.chapters
    # end if

    if disable_args or not selected:
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'chapters',
                'message': 'Choose chapters to download:',
                'choices': [
                    Choice('%d - %s' % (chap['id'], chap['title']))
                    for chap in self.app.crawler.chapters
                ],
                'validate': lambda a: True if a else (False, 'Select at least one chapter.'),
            }
        ])
        selected = [
            int(val.split(' ')[0])
            for val in answer['chapters']
        ]
    else:
        selected = [
            self.app.crawler.get_chapter_index_of(x)
            for x in selected if x
        ]
    # end if

    if times < 3 and len(selected) == 0:
        return self.get_range_from_chapters(times + 1)
    # end if

    selected = [
        x for x in selected
        if 1 <= x <= len(self.app.crawler.chapters)
    ]

    return selected
# end def
