# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler
import re


logger = logging.getLogger(__name__)


class RanobeLibCrawler(Crawler):
    base_url = 'https://ranobelib.me/'

    def read_novel_info(self):
        logger.info('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.manga-title h1')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('.manga__image img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        novel_link = soup.select_one("a[href*=author]")
        if novel_link:
            self.novel_author = novel_link.text.strip().title()
        # end if
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.select('.chapter-item')
        chapters.reverse()

        volumes = set()
        for a in chapters:
            chap_id = len(self.chapters) + 1

            vol_id = int(a['data-volume'])
            volumes.add(vol_id)

            link = a.select_one('a')
            chapter_title = re.sub(r'\s+', ' ', link.text).strip()
            if not chapter_title:
                chapter_title = 'Том %d. Глава %d' % (
                    int(vol_id), int(a['data-number']))
            # end if

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(link['href']),
                'title': chapter_title,
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        div = soup.select_one('.reader-container')
        return self.cleaner.extract_contents(div)
    # end def
# end class
