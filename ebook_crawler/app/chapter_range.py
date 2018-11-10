#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To select chapters to download
"""
from PyInquirer import prompt
from ..utils.validators import validateNumber

def chapter_range(app):
    length = len(app.crawler.chapters)
    vol_len = len(app.crawler.volumes)
    big_list_warn = '(warn: very big list)' if length > 50 else ''
    choices = {
        'Everything! (%d chapters)' % length: lambda x: x,
        'Custom range using URL': lambda x: range_using_urls(app),
        'Custom range using index': lambda x: range_using_index(app),
        'Select specific volumes (%d volumes)' % vol_len: lambda x: range_from_volumes(app),
        'Select specific chapters ' + big_list_warn: lambda x: range_from_chapters(app),
    }
    if length >= 20:
        choices.update({
            'First 10 chapters': lambda x: x[:10],
            'Last 10 chapters': lambda x: x[-10:],
        })
    # end if

    answer = prompt([
        {
            'type': 'list',
            'name': 'choice',
            'message': 'Which chapters to download?',
            'choices': choices.keys()
        },
    ])
    app.chapters = choices[answer['choice']](app.crawler.chapters) or []
    app.logger.debug('Selected chapters to download:')
    app.logger.debug(app.chapters)
    app.logger.info('%d chapters to be downloaded', len(app.chapters))

    if not len(app.chapters):
        raise Exception('No chapters selected')
    # end if
# end def

def range_using_urls(app):
    validator = lambda val: 'No such chapter found given the url' \
        if app.crawler.get_chapter_index_of(val) < 0 else True
    answer = prompt([
        {
            'type': 'input',
            'name': 'start',
            'message': 'Enter start url:',
            'validate': validator,
        },
        {
            'type': 'input',
            'name': 'stop',
            'message': 'Enter final url:',
            'validate': validator,
        },
    ])
    start = app.crawler.get_chapter_index_of(answer['start'])
    stop = app.crawler.get_chapter_index_of(answer['stop'])
    if stop < start:
        start, stop = stop, start
    # end if
    app.logger.debug('Selected range: %s to %s', start, stop)

    return app.crawler.chapters[start:(stop + 1)]
# end def

def range_using_index(app):
    length = len(app.crawler.chapters)
    answer = prompt([
        {
            'type': 'input',
            'name': 'start',
            'message': 'Enter start index (1 to %d):' % length,
            'validate': lambda val: validateNumber(val, 1, length),
            'filter': lambda val: int(val),
        },
    ])
    start = answer['start']
    answer = prompt([
        {
            'type': 'input',
            'name': 'stop',
            'message': 'Enter final index (%d to %d):' % (start, length),
            'validate': lambda val: validateNumber(val, start, length),
            'filter': lambda val: int(val),
        },
    ])
    stop = answer['stop']
    app.logger.debug('Selected range: %s to %s', start, stop)
    return app.crawler.chapters[(start - 1):stop]
# end def

def range_from_volumes(app, times=0):
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
                for vol in app.crawler.volumes
            ],
            'validate': lambda ans: True if len(ans) > 0 \
                else 'You must choose at least one volume.'
        }
    ])
    selected = [
        int(val.split(' ')[0])
        for val in answer['volumes']
    ]
    if times < 3 and len(selected) == 0:
        return range_from_volumes(app, times + 1)
    # end if

    return [
        chap for chap in app.crawler.chapters
        if selected.count(chap['volume']) > 0
    ]
# end def

def range_from_chapters(app, times=0):
    answer = prompt([
        {
            'type': 'checkbox',
            'name': 'chapters',
            'message': 'Choose chapters to download:',
            'choices': [
                { 'name': '%d - %s' % (chap['id'], chap['title']) }
                for chap in app.crawler.chapters
            ],
        }
    ])
    selected = [
        int(val.split(' ')[0])
        for val in answer['chapters']
    ]
    if times < 3 and len(selected) == 0:
        return range_from_chapters(app, times + 1)
    # end if

    return [
        chap for chap in app.crawler.chapters
        if selected.count(chap['id']) > 0
    ]
# end def
