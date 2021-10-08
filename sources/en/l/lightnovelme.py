# -*- coding: utf-8 -*-
import json
import logging
from concurrent.futures import Future
from urllib.parse import quote

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://lightnovels.me/api/search?keyword=%s&index=0&limit=20'
chapter_list_url = 'https://lightnovels.me/api/chapters?id=%d&index=%d&limit=%d'

class LightnovelMe(Crawler):
    base_url = [
        'https://lightnovels.me/'
    ]

    def search_novel(self, query):
        data = self.get_json(search_url % quote(query))
        
        results = []
        for item in data['results']:
            results.append({
                'title': item['title'],
                'url': 'https://lightnovels.me/novel' + item['slug'],
                'info': f"Author: {item['authorName']} | Latest: {item['lastChapter']}",
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        script = soup.select_one('script#__NEXT_DATA__')
        assert isinstance(script, Tag)
        data = json.loads(script.text)
        
        novel_info = data['props']['pageProps']['novelInfo']
        novel_id = novel_info['id']
        self.novel_title = novel_info['title']
        self.novel_cover = self.absolute_url(novel_info['image'])
        self.novel_author = ', '.join([
            x['name'] for x in data['props']['pageProps']['authors']
        ])

        latest_index = data['props']['pageProps']['cachedLatestChapters'][0]['chapter_index']
        data = self.get_json(chapter_list_url % (novel_id, 1, latest_index + 10))

        for i, item in enumerate(data['results']):
            chap_id = i + 1
            vol_id = i // 100 + 1
            if i % 100 == 0:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': item['chapter_name'],
                'url': self.absolute_url(item['slug']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        script = soup.select_one('script#__NEXT_DATA__')
        assert isinstance(script, Tag)
        data = json.loads(script.text)

        chapter_info = data['props']['pageProps']['cachedChapterInfo']
        content = str(chapter_info['content'])
        content = content.replace('\u003c', '<').replace('\u003e', '>')
        content = content.replace('<p>' + chapter_info['chapter_name'] + '</p>', '', 1)
        return content
    # end def

# end class
