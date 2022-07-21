# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode, urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class MTLNation(Crawler):
    base_url = [
        'https://mtlnation.com/'
    ]
    machine_translation = True

    def initialize(self):
        pass
    # end def

    def search_novel(self, query):
        data = self.get_json('https://api.mtlnation.com/api/v2/novels/?' + urlencode({
            'max_word_count': 0,
            'min_word_count':  0,
            'query': query,
            'sort': 'chapter_new',
        }))
        results = []
        for item in data['data']:
            results.append({
                'title': item['title'],
                'url': f"https://mtlnation.com/novel/{item['slug']}",
                'info': 'Chapters: %d | Rating: %d | Author: %s' % (
                    item['chapter_count'], item['rating'], item['author']),
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        slug = urlparse(self.novel_url).path.split('/')[-1]
        data = self.get_json(f'https://api.mtlnation.com/api/v2/novels/{slug}')

        self.novel_title = data['data']['title']
        self.novel_author = data['data']['author']
        self.novel_cover = 'https://api.mtlnation.com/media/' + data['data']['cover']

        data = self.get_json(f"https://api.mtlnation.com/api/v2/novels/{data['data']['id']}/chapters/")
        for item in data['data']:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if vol_id > len(self.volumes):
                self.volumes.append({'id':vol_id})
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': item['title'],
                'url': f"https://mtlnation.com/novel/{slug}/{item['slug']}",
                'data_url': f"https://api.mtlnation.com/api/v2/chapters/{slug}/{item['slug']}",
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        data = self.get_json(chapter['data_url'])
        return data['data']['content']
    # end def
# end class
