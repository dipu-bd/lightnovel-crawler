# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class WebnovelOnlineCrawler(Crawler):
    base_url = 'https://webnovel.online/'

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(['h1', 'h3', 'hr'])
    # end def
    
    def read_novel_info(self):
        url = self.novel_url
        soup = self.get_soup(url)

        img = soup.select_one('main img.cover')
        self.novel_title = img['title'].strip()
        self.novel_cover = self.absolute_url(img['src'])

        span = soup.select_one('header span.send-author-event')
        if span:
            self.novel_author = span.text.strip()
        # end if

        chap_id = 0
        for a in soup.select('#info a.on-navigate-part'):
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
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])

        strong = soup.select_one('#story-content strong')
        if strong and re.search(r'Chapter \d+', strong.text):
            chapter['title'] = strong.text.strip()
            logger.info('Updated title: %s', chapter['title'])
        # end if

        contents = soup.select_one('#story-content')
        return self.cleaner.extract_contents(contents)
    # end def
# end class
