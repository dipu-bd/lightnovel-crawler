# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlparse
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
novel_page = 'https://myoniyonitranslations.com/%s'


class MyOniyOniTranslation(Crawler):
    base_url = 'https://myoniyonitranslations.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        path_fragments = urlparse(self.novel_url).path.split('/')
        novel_hash = path_fragments[1]
        if novel_hash == 'category':
            novel_hash = path_fragments[2]
        # end if
        self.novel_url = novel_page % novel_hash

        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        if not soup.select_one('article.page.type-page'):
            a = soup.select_one('header.entry-header p span:nth-of-type(3) a')
            if not a:
                raise Exception(
                    'Fail to recognize url as a novel page: ' + self.novel_url)
            # end if
            self.novel_url = a['href']
            return self.read_novel_info()
        # end if

        self.novel_title = soup.select_one(
            'header.entry-header h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        possible_authors = []
        for p in soup.select('.x-container .x-column.x-1-2 p'):
            if re.match(r'author|trans|edit', p.text, re.I):
                possible_authors.append(p.text.strip())
            # end if
        # end for
        if len(possible_authors):
            self.novel_author = ', '.join(possible_authors)
        # end if
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('.x-container img.x-img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        accordian = soup.select('.x-container .x-accordion .x-accordion-group')
        if accordian:
            for div in accordian:
                a = div.select_one('a.x-accordion-toggle')
                vol_id = len(self.volumes) + 1
                self.volumes.append({
                    'id': vol_id,
                    'title': a.text.strip()
                })
                for chap in div.select('.x-accordion-body a'):
                    self.chapters.append({
                        'volume': vol_id,
                        'id': len(self.chapters) + 1,
                        'title': chap.text.strip(' []'),
                        'url': self.absolute_url(chap['href']),
                    })
                # end for
            # end for
        else:
            self.volumes.append({'id': 1})
            for a in soup.select('.entry-content p a'):
                possible_url = self.absolute_url(a['href'].lower())
                if not possible_url.startswith(self.novel_url):
                    continue
                # end if
                self.chapters.append({
                    'volume': 1,
                    'id': len(self.chapters) + 1,
                    'url': possible_url,
                    'title': a.text.strip(' []'),
                })
            # end for
        # end if

        logger.debug('%d chapters & %d volumes found',
                     len(self.chapters), len(self.volumes))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('article div.entry-content')
        for tag in contents.select('*'):
            if tag.name == 'hr':
                break
            # end if
            tag.extract()
        # end for
        self.bad_tags.append('div')
        self.clean_contents(contents)
        return str(contents)
    # end def
# end class
