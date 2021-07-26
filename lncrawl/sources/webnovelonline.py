# -*- coding: utf-8 -*-
import re
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class WebnovelOnlineCrawler(Crawler):
    base_url = 'https://webnovel.online/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url
        logger.debug('Visiting %s', url)
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
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        strong = soup.select_one('#story-content strong')
        if strong and re.search(r'Chapter \d+', strong.text):
            chapter['title'] = strong.text.strip()
            logger.info('Updated title: %s', chapter['title'])
        # end if

        self.bad_tags += ['h1', 'h3', 'hr']
        contents = soup.select_one('#story-content')
        return self.extract_contents(contents)
    # end def
# end class
