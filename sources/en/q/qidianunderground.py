# -*- coding: utf-8 -*-
'''
Decryptor: https://github.com/Pioverpie/privatebin-api/blob/master/privatebinapi/download.py
'''
import logging
import re
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlsplit

import regex
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_list_url = 'https://toc.qidianunderground.org/api/v1/pages/public'
chapter_list_url = 'https://toc.qidianunderground.org/api/v1/pages/public/%s/chapters'
chapter_body_url = '/?pasteid=%s'


class QidianComCrawler(Crawler):
    base_url = [
        'https://toc.qidianunderground.org/',
    ]

    def __init__(self):
        super().__init__()
        self.chapter_cache = {}
        self.set_header('Accept', 'application/json')
        self.executor = ThreadPoolExecutor(max_workers=1)

    @property
    def novel_list(self):
        if not hasattr(self, '_novel_list'):
            data = self.get_json(novel_list_url)
            self._novel_list = {x['ID']: x for x in data}
        return self._novel_list

    def search_novel(self, query):
        query = query.strip().lower()
        spaces = len(query.split(' '))
        query = regex.compile('(%s){e<=%d}' % (query, spaces))

        results = []
        for novel in self.novel_list.values():
            m = query.search(novel['Name'].lower())
            if m:
                last_update = datetime.fromtimestamp(novel['LastUpdated'])
                last_update = last_update.strftime('%Y-%m-%d %I:%M:%S %p')
                results.append({
                    'title': novel['Name'],
                    'url': chapter_list_url % novel['ID'],
                    'info': 'Last Updated: %s' % last_update,
                    'score': sum(len(x) for x in m.groups()),
                })
        return list(sorted(results, key=lambda x: -x['score']))[:10]

    def read_novel_info(self):
        novel_id = self.novel_url.split('/')[-2]
        self.novel_title = self.novel_list[novel_id]['Name']

        data = self.get_json(self.novel_url)
        for i, item in enumerate(data):
            vol_id = i + 1
            start_ch, final_ch = re.findall(r'(\d+) - (\d+)', item['Text'])[0]
            self.volumes.append({
                'id': vol_id,
                'title': 'Chapters %s - %s' % (start_ch, final_ch),
            })
            for j in range(int(start_ch), int(final_ch) + 1):
                self.chapters.append({
                    'id': j,
                    'volume': vol_id,
                    'url': item['Href'],
                })

    def download_chapter_body(self, chapter):
        from lncrawl.utils.pbincli import PasteV2

        url_data = urlsplit(chapter['url'])
        pasteHost = url_data.scheme + '://' + url_data.netloc
        pasteId = url_data.query
        passphrase = url_data.fragment

        if pasteId in self.chapter_cache:
            soup = self.chapter_cache[pasteId]
        else:
            data = self.get_json(pasteHost + (chapter_body_url % pasteId))
            paste = PasteV2()
            paste.setHash(passphrase)
            paste.loadJSON(data)
            paste.decrypt()
            soup = self.make_soup(paste.getText())
            self.chapter_cache[pasteId] = soup

        a = soup.select_one('#toc a[href*="chapter-%d"]' % chapter['id'])
        chapter['title'] = a.text.strip()
        logger.debug(chapter['title'])

        logger.debug('Chapter Id: %s', a['href'])
        contents = soup.find('div', attrs={'id': a['href'][1:]})
        contents = contents.find('div', attrs={'class': 'well'})
        for bad in contents.select('h2, br'):
            bad.extract()

        body = contents.text.split('\n\n')
        return '<p>' + '</p><p>'.join(body) + '</p>'
