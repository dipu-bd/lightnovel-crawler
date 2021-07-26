# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.novelall.com/search/?name=%s'


class NovelAllCrawler(Crawler):
    base_url = 'https://www.novelall.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('.cover-info p.title a')[:20]:
            url = self.absolute_url(a['href'])
            results.append({
                'url': url,
                'title': a.text.strip(),
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url + '?waring=1')

        self.novel_title = soup.find(
            'div', {"class": "manga-detail"}).find('h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('div', {"class": "manga-detail"}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.find(
            'div', {"class": "detail-info"}).find('a').text.split(',')
        if len(author) == 2:
            self.novel_author = author[0] + ' (' + author[1] + ')'
        else:
            self.novel_author = ' '.join(author)
        # end if
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find(
            'div', {"class": "manga-detailchapter"}).findAll('a', title=True)
        chapters.reverse()
        for a in chapters:
            for span in a.findAll('span'):
                span.extract()
            # end for
        # end for

        for x in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': self.absolute_url(x['href']),
                'title': x['title'] or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.find('div', {'class': 'reading-box'})
        self.clean_contents(contents)
        return str(contents)
    # end def
# end class
