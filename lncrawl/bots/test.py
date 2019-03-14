#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The purpose of this bot is to test the application and crawlers.
Tests should include:
  - Overall application flow: DONE
  - Each methods implemented inside crawlers
  - Each utility libraries
  - Each binder methods
Test should look for:
  - Exceptions
  - Unexpected outputs
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
            self.test_app_flow()
        except Exception:
            traceback.print_exc()
        # end try
    # end def

    def test_app_flow(self):
        app = App()
        print('App instance: OK')

        app.initialize()
        print('App initialize: OK')

        app.user_input = 'martial'
        app.init_search()
        print('Init search: OK')

        if not app.crawler:
            print(len(app.crawler_links), 'available crawlers to search')
            app.crawler_links = app.crawler_links[:2]
            print('Selected crawler:', str(app.crawler_links[0]))

            app.search_novel()
            print('Search: %d results found' % len(app.search_results))

            source = app.search_results[0]
            print('Top result: %s with %d sources' %
                  (source['title'], len(source['novels'])))

            novel_url = source['novels'][0]['url']
            print('Top novel:', novel_url)

            app.init_crawler(novel_url)
            print('Init crawler: OK')
        # end if

        if app.can_do('login'):
            print('Login: enabled')
        # end if

        app.get_novel_info()
        print('Novel info: OK')
        print('Author:', app.crawler.novel_author)
        print('Cover:', app.crawler.novel_cover)
        print('Title:', app.crawler.novel_title)
        print('Volume count:', len(app.crawler.volumes))
        print('Chapter count:', len(app.crawler.chapters))

        os.makedirs(app.output_path, exist_ok=True)
        print('Output path:', app.output_path)

        app.chapters = app.crawler.chapters[:10]
        app.output_formats = {}
        app.pack_by_volume = False

        app.start_download()
        print('Download: OK')

        app.bind_books()
        print('Bindings: OK')

        app.destroy()
        print('Destroy: OK')

        print('-' * 6, 'Test Passed', '-' * 6)
    # end def
# end class
