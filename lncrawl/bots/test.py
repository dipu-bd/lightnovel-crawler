#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The purpose of this bot is to test the application and crawlers
"""
import re
import os
import sys
import shutil
import logging
import textwrap
import traceback
from PyInquirer import prompt

from ..core import display
from ..core.app import App
from ..core.arguments import get_args
from ..assets.icons import Icons
from ..spiders import crawler_list
from ..binders import available_formats
from ..utils.kindlegen_download import download_kindlegen, retrieve_kindlegen


class TestBot:
    def start(self):
        try:
            for link in crawler_list.keys():
                print('=' * 80)
                print('>>>', link)
                print('=' * 80)

                if link not in test_user_inputs:
                    raise Exception('No inputs found: %s' % link)
                # end if

                for entry in test_user_inputs[link]:
                    print('-' * 5, 'Input:', entry, '-' * 5)
                    self.test_crawler(link, entry)
                    print()
                # end for

                print('\n')
            # end for
        except Exception:
            print(traceback.format_exc())
            exit(1)
        # end try
    # end def

    def test_crawler(self, link, user_input):
        app = App()
        print('App instance: OK')

        app.initialize()
        print('App initialize: DONE')

        app.user_input = user_input
        app.init_search()
        print('Init search: DONE')

        if not app.crawler:
            print(len(app.crawler_links), 'available crawlers to search')
            app.crawler_links = [link]
            print('Selected crawler:', link)

            app.search_novel()
            print('Search: %d results found' % len(app.search_results))

            source = app.search_results[0]
            print('Top result: %s with %d sources' %
                  (source['title'], len(source['novels'])))

            novel_url = source['novels'][0]['url']
            print('Top novel:', novel_url)

            app.init_crawler(novel_url)
            print('Init crawler: DONE')
        # end if

        if not app.crawler:
            raise Exception('No crawler initialized')
        # end if

        if app.can_do('login'):
            print('Login: enabled')
        # end if

        app.get_novel_info()
        print('Title:', app.crawler.novel_title)
        print('Cover:', app.crawler.novel_cover)
        print('Author:', app.crawler.novel_author)

        if not app.crawler.novel_title:
            raise Exception('No novel title')
        # end if

        print('Novel info: DONE')

        os.makedirs(app.output_path, exist_ok=True)
        print('Output path:', app.output_path)

        if len(app.crawler.volumes) == 0:
            raise Exception('Empty volume list')
        # end if

        if len(app.crawler.chapters) == 0:
            raise Exception('Empty chapter list')
        # end if

        app.chapters = app.crawler.chapters[:1]
        app.output_formats = {}
        app.pack_by_volume = False

        app.start_download()
        print('Download: DONE')

        if len(app.chapters[0]['body']) < 50:
            raise Exception('Empty body')
        # end if

        app.bind_books()
        print('Bindings: DONE')

        app.destroy()
        print('Destroy: DONE')

        print('-' * 6, 'Test Passed', '-' * 6)
    # end def
# end class


test_user_inputs = {
    'http://fullnovel.live/': [
        'http://fullnovel.live/novel-a-will-eternal',
        'will eternal',
    ],
    'http://gravitytales.com/': [
        'http://gravitytales.com/novel/chaotic-lightning-cultivation',
    ],
    'http://novelfull.com/': [
        'http://novelfull.com/hidden-marriage.html',
        'hidden',
    ],
    'http://www.machinenoveltranslation.com/': [
        'http://www.machinenoveltranslation.com/a-thought-through-eternity',
    ],
    'http://zenithnovels.com/': [
        'http://zenithnovels.com/infinity-armament/',
    ],
    'https://anythingnovel.com/': [
        'https://anythingnovel.com/novel/king-of-gods/',
    ],
    'https://boxnovel.com/': [
        'https://boxnovel.com/novel/the-rest-of-my-life-is-for-you/',
        'cultivation chat',
    ],
    'https://comrademao.com/': [
        'https://comrademao.com/novel/against-the-gods/',
    ],
    'https://crescentmoon.blog/': [
        'https://crescentmoon.blog/dark-blue-and-moonlight/',
    ],
    'https://litnet.com/': [
        'https://litnet.com/en/book/candy-lips-1-b106232',
        'candy lips',
    ],
    'https://lnindo.org/': [
        'https://lnindo.org/novel/true-martial-world/',
    ],
    'https://lnmtl.com/': [
        'https://lnmtl.com/novel/the-strongest-dan-god',
    ],
    'https://m.chinesefantasynovels.com/': [
        'https://m.chinesefantasynovels.com/3838/',
    ],
    'https://m.novelspread.com/': [
        'https://m.novelspread.com/novel/the-legend-of-the-concubine-s-daughter-minglan',
    ],
    'https://m.romanticlovebooks.com/': [
        'https://m.romanticlovebooks.com/xuanhuan/207.html',
    ],
    'https://m.wuxiaworld.co/': [
        'https://m.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/',
        'sword',
    ],
    'https://meionovel.com/': [
        'https://meionovel.com/novel/the-legendary-mechanic/',
    ],
    'https://mtled-novels.com/': [
        'https://mtled-novels.com/novels/ancient-demon-dragon-emperor',
        'dragon'
    ],
    'https://novelonlinefree.info/': [
        'https://novelonlinefree.info/novel/martial_world',
        'martial'
    ],
    'https://novelplanet.com/': [
        'https://novelplanet.com/Novel/Returning-from-the-Immortal-World',
        'immortal'
    ],
    'https://volarenovels.com/': [
        'https://volarenovels.com/adorable-creature-attacks/',
    ],
    'https://webnovel.online/': [
        'https://webnovel.online/full-marks-hidden-marriage-pick-up-a-son-get-a-free-husband',
    ],
    'https://wuxiaworld.online/': [
        'https://wuxiaworld.online/trial-marriage-husband-need-to-work-hard',
        'marriage',
    ],
    'https://www.idqidian.us/': [
        'https://www.idqidian.us/novel/peerless-martial-god/'
    ],
    'https://www.novelall.com/': [
        'https://www.novelall.com/novel/Virtual-World-Close-Combat-Mage.html',
        'combat'
    ],
    'https://www.novelspread.com/': [
        'https://www.novelspread.com/novel/the-legend-of-the-concubine-s-daughter-minglan'
    ],
    'https://www.noveluniverse.com/': [
        'https://www.noveluniverse.com/index/novel/info/id/15.html'
    ],
    'https://www.novelv.com/': [
        'https://www.novelv.com/0/349/'
    ],
    'https://www.readlightnovel.org/': [
        'https://www.readlightnovel.org/martial-god-asura'
    ],
    'https://www.romanticlovebooks.com/': [
        'https://www.romanticlovebooks.com/xianxia/251.html'
    ],
    'https://www.royalroad.com/': [
        'https://www.royalroad.com/fiction/21220/mother-of-learning',
        'mother'
    ],
    'https://www.scribblehub.com/': [
        'https://www.scribblehub.com/series/10442/world-keeper/',
        'cultivation'
    ],
    'https://www.webnovel.com/': [
        'https://www.webnovel.com/book/8212987205006305/Trial-Marriage-Husband%3A-Need-to-Work-Hard',
        'martial',
    ],
    'https://www.worldnovel.online/': [
        'https://www.worldnovel.online/novel/pan-long/',
        'cultivation'
    ],
    'https://www.wuxiaworld.co/': [
        'https://www.wuxiaworld.co/Reincarnation-Of-The-Strongest-Sword-God/',
        'sword'
    ],
    'https://www.wuxiaworld.com/': [
        'https://www.wuxiaworld.com/novel/martial-god-asura',
        'martial',
    ],
}
