#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The purpose of this bot is to test the application and crawlers
"""
import io
import logging
import os
import platform
import re
import shutil
import sys
import textwrap
import time
import traceback
from datetime import datetime
from random import random

from PyInquirer import prompt

from ..assets.icons import Icons
from ..binders import available_formats
from ..core import display
from ..core.app import App
from ..core.arguments import get_args
from ..spiders import crawler_list
from ..utils.cfscrape import CloudflareCaptchaError
from ..utils.kindlegen_download import download_kindlegen, retrieve_kindlegen
from ..utils.make_github_issue import find_issues, post_issue

# For colorama
sys.stdout = io.TextIOWrapper(sys.stdout.detach(),
                              encoding=sys.stdout.encoding,
                              errors='ignore',
                              line_buffering=True)


class TestBot:
    allerrors = dict()

    def start(self):
        try:
            randomized = sorted(crawler_list.keys(), key=lambda x: random())
            for index, link in enumerate(randomized):
                print('=' * 80)
                print('>>>', index, ':', link)
                print('=' * 80)

                if link not in self.test_user_inputs:
                    print('No inputs found: %s\n' % link)
                    continue
                # end if

                for entry in self.test_user_inputs[link]:
                    try:
                        print('-' * 5, 'Input:', entry, '-' * 5)
                        self.test_crawler(link, entry)
                        print()
                    except CloudflareCaptchaError:
                        traceback.print_exc()
                        break
                    except Exception as err:
                        traceback.print_exc()
                        traces = traceback.format_tb(err.__traceback__)
                        if link not in self.allerrors:
                            self.allerrors[link] = []
                        # end if
                        self.allerrors[link].append(
                            '> Input: %s\n%s\n%s' % (
                                entry, err, ''.join(traces))
                        )
                    # end try
                # end for
                print('\n')
            # end for
            exit(0)
        except:
            traceback.print_exc()
        finally:
            if len(self.allerrors):
                message = self.error_message()
                print(message)
                self.post_on_github(message)
            # end if
            if len([x for x in self.allerrors.keys() if x not in self.allowed_failures]):
                exit(1)
            # end if
        # end try
    # end def

    def post_on_github(self, message):
        if sys.version_info.minor != 6:
            print('Not Python 3.6... skipping.')
            return
        # end if

        # Check if there is already an issue younger than a week
        issues = find_issues('bot-report')
        if len(issues):
            time = int(issues[0]['title'].split('~')[-1].strip())
            diff = datetime.utcnow().timestamp() - time
            if diff < 7 * 24 * 3600:
                print('Detected an open issue younger than a week... skipping.')
                return
            # end if
        # end if

        # Create new issue with appropriate label
        title = '[Test Bot][Python %d.%d][%s] Report ~ %s' % (
            sys.version_info.major,
            sys.version_info.minor,
            platform.system(),
            datetime.utcnow().strftime('%s')
        )
        post_issue(
            title,
            '```\n%s\n```' % message,
            ['bot-report']
        )
    # end def

    def error_message(self):
        output = '=' * 80 + '\n'
        output += 'Failed sources (%d):\n' % len(self.allerrors.keys())
        output += '\n'.join(sorted(self.allerrors.keys())) + '\n'
        output += '-' * 80 + '\n\n'

        num = 0
        for key in sorted(self.allerrors.keys()):
            for err in set(self.allerrors[key]):
                num += 1
                output += '-' * 80 + '\n'
                output += 'Error #%d: %s\n' % (num, key)
                output += '-' * 80 + '\n'
                output += err + '\n'
            # end for
        # end for

        output += '\n' + '=' * 80 + '\n'
        return output
    # end_def

    def test_crawler(self, link, user_input):
        app = App()
        print('App instance: OK')

        app.initialize()
        print('App initialize: DONE')

        app.user_input = user_input
        app.init_search()
        print('Init search: DONE')

        if not app.crawler:
            if link not in app.crawler_links:
                print('Search is not supported for', link)
                return
            # end if

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

            app.get_novel_info()
            print('Novel info: DONE')
            if not app.crawler.novel_title:
                raise Exception('No novel title')
                # end if
            return
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

        app.chapters = app.crawler.chapters[:2]
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

    test_user_inputs = {
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
        'https://bestlightnovel.com/': [
            'https://bestlightnovel.com/novel_888103800',
            'martial'
        ],
        'https://novelplanet.com/': [
            'https://novelplanet.com/Novel/Returning-from-the-Immortal-World',
            'immortal'
        ],
        'https://www.volarenovels.com/': [
            'https://www.volarenovels.com/novel/adorable-creature-attacks',
        ],
        'https://webnovel.online/': [
            'https://webnovel.online/full-marks-hidden-marriage-pick-up-a-son-get-a-free-husband',
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
        'https://www.readlightnovel.org/': [
            'https://www.readlightnovel.org/top-furious-doctor-soldier'
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
        'https://creativenovels.com/': [
            'https://creativenovels.com/novel/136/eternal-reverence/',
        ],
        'https://www.tapread.com/': [
            'https://www.tapread.com/book/detail?bookId=80',
        ],
        'https://4scanlation.xyz/': [
            'https://4scanlation.xyz/instant-messiah/',
        ],
        'https://yukinovel.me/': [
            'https://yukinovel.me/novel/the-second-coming-of-avarice/',
        ],
        'https://readnovelfull.com/': [
            'https://readnovelfull.com/lord-of-all-realms.html',
            'cultivation'
        ],
        'https://myoniyonitranslations.com/': [
            'https://myoniyonitranslations.com/top-management/',
            'https://myoniyonitranslations.com/lm-chapter-277-279/',
            'https://myoniyonitranslations.com/category/kill-the-hero/'
        ],
        'https://babelnovel.com/': [
            'https://babelnovel.com/books/poison-genius-consort',
            'martial god AsurA'
        ],
        'https://wuxiaworld.online/': [
            'https://wuxiaworld.online/trial-marriage-husband-need-to-work-hard',
            'cultivation',
        ],
        'https://www.novelv.com/': [
            'https://www.novelv.com/0/349/'
        ],
        'http://fullnovel.live/': [
            'http://fullnovel.live/novel-a-will-eternal',
            'will eternal',
        ],
        'https://www.noveluniverse.com/': [
            'https://www.noveluniverse.com/index/novel/info/id/15.html'
        ],
        'https://novelraw.blogspot.com/': [
            'https://novelraw.blogspot.com/2019/03/dragon-king-son-in-law-mtl.html'
        ],
        'https://light-novel.online/': [
            'https://light-novel.online/great-tyrannical-deity',
            'tyrannical'
        ],
        'https://www.rebirth.online/': [
            'https://www.rebirth.online/novel/the-good-for-nothing-seventh-young-lady'
        ],
        'https://www.wattpad.com/': [
            'https://www.wattpad.com/story/87505567-loving-mr-jerkface-%E2%9C%94%EF%B8%8F'
        ],
        'https://novelgo.id/': [
            'https://novelgo.id/novel/the-mightiest-leveling-system/'
        ]
    }

    allowed_failures = [
        'https://4scanlation.xyz/',
        'https://m.chinesefantasynovels.com/',
    ]
# end class
