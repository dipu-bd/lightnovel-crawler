import sys

from PyInquirer import prompt

from .arguments import get_args


def get_novel_url():
    url = get_args().novel_page
    if url and url.startswith('http'):
        return url
    # end if

    answer = prompt([
        {
            'type': 'input',
            'name': 'novel',
            'message': 'Enter the url of your novel:',
            'validate': lambda val: 'Url should be not be empty'
            if len(val) == 0 else True,
        },
    ])

    return answer['novel'].strip()
# end def


def force_replace_old():
    if get_args().force:
        return get_args().force >= 1
    # end if
    answer = prompt([
        {
            'type': 'confirm',
            'name': 'force',
            'message': 'Detected existing folder. Replace it?',
            'default': False,
        },
    ])
    return answer['force']
# end def


def login_info():
    args = get_args()
    if args.login:
        return args.login
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
        return answer['email'], answer['password']
    # end if
    return None
# end if


def download_selection(chapter_count, volume_count):
    keys = ['all', 'last', 'first', 'page', 'range', 'volumes', 'chapters']

    arg = get_args()
    for key in keys:
        if arg.__getattribute__(key):
            return key
        # end if
    # end if

    big_list_warn = '(warn: very big list)' if chapter_count > 50 else ''

    choices = [
        'Everything! (%d chapters)' % chapter_count,
        'Last 10 chapters',
        'First 10 chapters',
        'Custom range using URL',
        'Custom range using index',
        'Select specific volumes (%d volumes)' % volume_count,
        'Select specific chapters ' + big_list_warn,
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

    return keys[choices.index(answer['choice'])]
# end def


def range_using_urls(crawler):
    start_url, stop_url = get_args().page

    if not (start_url and stop_url):
        def validator(val):
            try:
                if crawler.get_chapter_index_of(val) > 0:
                    return True
            except:
                pass
            return 'No such chapter found given the url'
        # end def
        answer = prompt([
            {
                'type': 'input',
                'name': 'start_url',
                'message': 'Enter start url:',
                'validate': validator,
            },
            {
                'type': 'input',
                'name': 'stop_url',
                'message': 'Enter final url:',
                'validate': validator,
            },
        ])
        start_url = answer['start_url']
        stop_url = answer['stop_url']
    # end if

    start = crawler.get_chapter_index_of(start_url) - 1
    stop = crawler.get_chapter_index_of(stop_url) - 1

    return (start, stop) if start < stop else (stop, start)
# end def


def range_using_index(chapter_count):
    start, stop = get_args().range

    if not (start and stop):
        def validator(val):
            try:
                if 1 <= int(val) <= chapter_count:
                    return True
            except:
                pass
            return 'Please enter an integer between 1 and %d' % chapter_count
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


def range_from_volumes(volumes, times=0):
    selected = None

    if times == 0:
        selected = get_args().volumes
    # end if

    if not selected:
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'volumes',
                'message': 'Choose volumes to download:',
                'choices': [
                    {
                        'name': '%d - %s [%d chapters]' % (
                            vol['id'], vol['title'], vol['chapter_count'])
                    }
                    for vol in volumes
                ],
                'validate': lambda ans: True if len(ans) > 0
                else 'You must choose at least one volume.'
            }
        ])
        selected = [
            int(val.split(' ')[0])
            for val in answer['volumes']
        ]
    # end if

    if times < 3 and len(selected) == 0:
        return range_from_volumes(volumes, times + 1)
    # end if

    return selected
# end def


def range_from_chapters(crawler, times=0):
    selected = None

    if times == 0:
        selected = get_args().chapters
    # end if

    if not selected:
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'chapters',
                'message': 'Choose chapters to download:',
                'choices': [
                    {'name': '%d - %s' % (chap['id'], chap['title'])}
                    for chap in crawler.chapters
                ],
            }
        ])
        selected = [
            int(val.split(' ')[0])
            for val in answer['chapters']
        ]
    else:
        selected = [
            crawler.get_chapter_index_of(x)
            for x in selected if x
        ]
    # end if

    if times < 3 and len(selected) == 0:
        return range_from_chapters(crawler, times + 1)
    # end if

    selected = [
        x for x in selected
        if 1 <= x <= len(crawler.chapters)
    ]

    return selected
# end def

def pack_by_volume():
    if len(sys.argv) > 1:
        return get_args().byvol
    # end if

    answer= prompt([
        {
            'type': 'confirm',
            'name': 'volume',
            'message': 'Generate separate files for each volumes?',
            'default': False,
        },
    ])
    return answer['volume']
# end def
