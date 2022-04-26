# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

ajaxchapter_url = 'https://www.1ksy.com/home/index/ajaxchapter'


class OneKsyCrawler(Crawler):
    base_url = [
        'https://m.1ksy.com/',
        'https://www.1ksy.com/',
    ]

    def initialize(self):
        self.home_url = 'https://www.1ksy.com/'
    # end def

    def read_novel_info(self):
        url = self.novel_url.replace(
            'https://m.1ksy', 'https://www.1ksy')
        soup = self.get_soup(url)

        possible_title = soup.select_one('body > div.jieshao > div.rt > h1')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('body > div > div.lf > img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        possible_novel_author = soup.select_one('meta[property="og:novel:author"]')
        if possible_novel_author:
            self.novel_author = possible_novel_author['content']
        logger.info('Novel author: %s', self.novel_author)

        chap_id = 0
        for a in soup.select('body > div.mulu ul')[-1].select('li a'):
            vol_id = chap_id // 100 + 1
            if vol_id > len(self.volumes):
                self.volumes.append({
                    'id': vol_id,
                    'title': 'Volume %d' % vol_id
                })
            # end if

            chap_id += 1
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a['title'],
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('#content')
        return self.cleaner.extract_contents(contents)
    # end def
# end class
