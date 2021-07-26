# -*- coding: utf-8 -*-
import json
import logging
import re

from slugify import slugify

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://novelplanet.com/NovelList?order=mostpopular&name=%s'


class NovelPlanetCrawler(Crawler):
    base_url = 'https://novelplanet.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('section a.title').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.post-previewInDetails img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for span in soup.find_all("span", {"class": "infoLabel"}):
            if span.text == 'Author:':
                author = span.findNext('a').text
                author2 = span.findNext('a').findNext('a').text
        # check if author word is found in second <p>
        if (author2 != 'Ongoing') or (author2 != 'Completed'):
            self.novel_author = author + ' (' + author2 + ')'
        else:
            self.novel_author = author
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find_all('div', {'class': 'rowChapter'})
        chapters.reverse()

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
                'url': self.absolute_url(x.find('a')['href']),
                'title': x.find('a')['title'] or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('#divReadContent')
        # self.clean_contents(content)
        if soup.select_one('h4').text:
            chapter['title'] = soup.select_one('h4').text
        else:
            if chapter['title'].startswith('Read'):
                chapter['title'].replace('Read Novel ', '')
            else:
                chapter['title'] = chapter['title']
            # end if
        # end if

        for ads in contents.findAll('div', {"style": 'text-align: center; margin-bottom: 10px'}):
            ads.extract()

        return str(contents)

        # return ''.join([
        #    str(p).strip()
        #    for p in content.select('p')
        #    if p.text.strip()
        # ])
    # end def
# end class
