# -*- coding: utf-8 -*-
import json
import math
import logging
import re

import js2py
from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_list_url = 'https://api.rewayat.club/api/chapters/%s/?ordering=number&page=%d'
chapter_body_url = 'https://rewayat.club/novel/%s/%d'

class RewayatClubCrawler(Crawler):
    base_url = 'https://rewayat.club/'

    def read_novel_info(self):
        self.is_rtl = True

        soup = self.get_soup(self.novel_url)
        script = soup.find(lambda tag: isinstance(tag, Tag) and tag.name == 'script' and tag.text.startswith('window.__NUXT__'))
        assert isinstance(script, Tag)

        data = js2py.eval_js(script.text).to_dict()

        novel_info = data['fetch'][0]['novel']
        pagination = data['fetch'][1]['pagination']
        per_page = len(data['fetch'][1]['chapters'])

        self.novel_title = novel_info['arabic']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = 'https://api.rewayat.club' + novel_info['poster_url']
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = ', '.join([x['username'] for x in novel_info['contributors']])
        logger.info('Novel author: %s', self.novel_author)

        novel_slug = novel_info['slug']
        logger.info('Novel slug: %s', novel_slug)

        total_items = pagination['count']
        total_pages = math.ceil(total_items / per_page)
        logger.info('Total pages: %d', total_pages)
        
        futures = []
        for page in range(total_pages):
            url = chapter_list_url % (novel_slug, page + 1)
            f = self.executor.submit(self.get_json, url)
            futures.append(f)
        # end for

        for f in futures:
            data = f.result()
            for item in data['results']:
                chap_id = 1 + len(self.chapters)
                vol_id = 1 + len(self.chapters) // 100
                if len(self.chapters) % 100 == 0:
                    self.volumes.append({ 'id': vol_id })
                # end if
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': item['title'],
                    'url': chapter_body_url % (novel_slug, item['number']),
                })
        # end for
    # end def
    
    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        script = soup.find(lambda tag: isinstance(tag, Tag) and tag.name == 'script' and tag.text.startswith('window.__NUXT__'))
        assert isinstance(script, Tag)

        data = js2py.eval_js(script.text).to_dict()

        contents = data['fetch'][0]['contentParts']
        contents = [x['content'] for y in contents for x in y]

        self.bad_tags = []
        self.bad_css = ['.code-block']
        html = '\n'.join(contents)
        html = html.replace('<span>', '').replace('</span>', '')
        body = self.make_soup(html).find('body')
        return self.extract_contents(body)
    # end def
# end class
