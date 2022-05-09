# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class VeraTales(Crawler):
    base_url = 'https://veratales.com/'

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1").text.strip()
        logger.info('Novel title: %s', self.novel_title)

        #self.novel_author= soup.find("div",{"class":"novel-author-info"}).find("h4").text.strip()
        self.novel_author=''
        logger.info('%s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.card-header a img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        
        chapters = soup.select('table td a')
        chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.reader-content')
        for bad in contents.select('h3, .code-block, script, .adsbygoogle'):
            bad.extract()

        return self.cleaner.extract_contents(contents)
    # end def
# end class