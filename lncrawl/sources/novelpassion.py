# -*- coding: utf-8 -*-
import re
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://www.novelpassion.com/search?keyword=%s'


class NovelPassion(Crawler):
    base_url = 'https://www.novelpassion.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '%20')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('div.lh1d5'):
            a = tab.select_one('a')
            votes = tab.select_one('span[class="g_star"]')['title']
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': 'Rating: %s' % (votes),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        img = soup.select_one('div.nw i.g_thumb img')
        self.novel_title = img['alt'].strip()
        self.novel_cover = self.absolute_url(img['src'])

        span = soup.select_one('div.dns a.stq')
        if span:
            self.novel_author = span.text.strip()
        # end if

        chap_id = 0
        for a in soup.select('#stq a.c_000'):
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
                'title': ('Chapter %d' % chap_id),
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        strong = soup.select_one('.cha-words strong')
        if strong and re.search(r'Chapter \d+', strong.text):
            chapter['title'] = strong.text.strip()
            logger.info('Updated title: %s', chapter['title'])
        # end if

        self.bad_tags += ['h1', 'h3', 'hr']
        contents = soup.select_one('.cha-words')
        return self.extract_contents(contents)
    # end def
# end class
