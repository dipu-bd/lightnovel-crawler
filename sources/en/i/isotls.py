# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class IsotlsCrawler(Crawler):
    base_url = [
        'https://isotls.com/',
        'https://www.isotls.com/',
    ]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_cover = soup.select_one('meta[property="og:image"]')
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover['content'])

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title['content']

        possible_novel_author = soup.select_one('meta[name="twitter:data1"]')
        if possible_novel_author:
            self.novel_author = possible_novel_author['content']

        for a in soup.select('main section div:nth-child(2) ul li a'):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select('article p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
