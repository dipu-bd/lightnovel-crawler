# -*- coding: utf-8 -*-
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)


class TomoTransCrawler(Crawler):
    base_url = 'https://tomotranslations.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('article h1.title').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('article figure.wp-block-image img')['data-orig-file'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = 'Tomo Translations'
        logger.info('Novel author: %s', self.novel_author)

        volumes = set()
        for a in soup.select('article section.entry a[href^="%s"]' % self.home_url):
            chap_id = len(self.chapters) + 1
            chap_url = self.absolute_url(a['href'])
            possible_vol = re.findall(r'-volume-(\d+)-', chap_url)
            if not len(possible_vol):
                continue
            # end if
            vol_id = int(possible_vol[0])
            volumes.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  chap_url,
                'title': a.text.strip(),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body = ''
        for tag in soup.select('article section.entry > *'):
            if tag.name == 'hr' and tag.has_attr("class") and 'is-style-dots' in tag.get('class'):
                body += '<p>—————–</p>'
            elif tag.name == 'p':
                if tag.find('strong'):
                    chapter['title'] = tag.text.strip()
                elif tag.find('a') and re.match(r'Previous|Next', tag.find('a').text):
                    pass
                else:
                    body += str(tag)
                # end if
            # end if
        # end for

        return body
    # end def
# end class
