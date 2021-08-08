# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'http://fastnovel.net/search/%s'

class FastNovel(Crawler):
    base_url = 'http://fastnovel.net/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '%20')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.film-item'):
            a = tab.select_one('a')
            latest = tab.select_one('label.current-status span.process').text
            results.append({
                'title': a['title'],
                'url': self.absolute_url(a['href']),
                'info': '%s' % (latest),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.name').text
        logger.info('Novel title: %s', self.novel_title)

        author = soup.find_all(href=re.compile('author'))
        if len(author) == 2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        else:
            self.novel_author = author[0].text
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('.book-cover')['data-original'])
        logger.info('Novel cover: %s', self.novel_cover)

        for div in soup.select('.block-film #list-chapters .book'):
            vol_title = div.select_one('.title a').text
            vol_id = [int(x) for x in re.findall(r'\d+', vol_title)]
            vol_id = vol_id[0] if len(vol_id) else len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })

            for a in div.select('ul.list-chapters li.col-sm-5 a'):
                ch_title = a.text
                ch_id = [int(x) for x in re.findall(r'\d+', ch_title)]
                ch_id = ch_id[0] if len(ch_id) else len(self.chapters) + 1
                self.chapters.append({
                    'id': ch_id,
                    'volume': vol_id,
                    'title': ch_title,
                    'url':  self.absolute_url(a['href']),
                })
            # end for
        # end for

        logger.debug('%d chapters and %d volumes found',
                     len(self.chapters), len(self.volumes))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('#chapter-body')
        # end for

        return str(contents)
    # end def

    def format_text(self, text):
        '''formats the text and remove bad characters'''
        text = re.sub(r'\u00ad', '', text, flags=re.UNICODE)
        text = re.sub(r'\u201e[, ]*', '&ldquo;', text, flags=re.UNICODE)
        text = re.sub(r'\u201d[, ]*', '&rdquo;', text, flags=re.UNICODE)
        text = re.sub(r'[ ]*,[ ]+', ', ', text, flags=re.UNICODE)
        return text.strip()
    # end def
# end class
