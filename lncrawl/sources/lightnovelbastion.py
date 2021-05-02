# -*- coding: utf-8 -*-
import json
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import quote_plus

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://lightnovelbastion.com/?s=%s'
chapter_list_url = 'https://lightnovelbastion.com/wp-admin/admin-ajax.php'


class LightNovelBastion(Crawler):
    base_url = 'https://lightnovelbastion.com/'

    # def search_novel(self, query):
    #     query = quote_plus(query.lower())
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for a in soup.select('#loop-content .post-title a'):
    #         results.append({
    #             'title': a['title'].strip(),
    #             'url': self.absolute_url(a['href']),
    #         })
    #     # end for

    #     return results
    # # end def

    def initialize(self):
        self.executor = ThreadPoolExecutor(1)

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = ' '.join([
            str(x)
            for x in soup.select_one('.post-title').select_one('h1, h2, h3, h4').contents
            if not x.name
        ]).strip()
        logger.info('Novel title: %s', self.novel_title)

        probable_img = soup.select_one('.summary_image img')
        if probable_img:
            self.novel_cover = self.absolute_url(probable_img['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select('.author-content a')
        if len(author) == 2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        else:
            self.novel_author = author[0].text
        logger.info('Novel author: %s', self.novel_author)

        if len(soup.select('ul.version-chap li.has-child li.wp-manga-chapter')):
            logger.debug('Has volume definitions')
            for li in reversed(soup.select('ul.version-chap li.has-child')):
                vol_id = len(self.volumes) + 1
                vol_title = li.select_one('a.has-child').text.strip()
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
                for a in reversed(li.select('ul.sub-chap li.wp-manga-chapter a')):
                    chap_id = len(self.chapters) + 1
                    self.chapters.append({
                        'id': chap_id,
                        'volume': vol_id,
                        'title': a.text.strip(),
                        'url':  self.absolute_url(a['href']),
                    })
                # end for
            # end for
        else:
            logger.debug('Has no volume definitions')
            volumes = set([])
            for a in reversed(soup.select('.wp-manga-chapter a')):
                chap_id = len(self.chapters) + 1
                vol_id = len(self.chapters) // 100 + 1
                volumes.add(vol_id)
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url':  self.absolute_url(a['href']),
                })
            # end for
            self.volumes = [{'id': x} for x in volumes]
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.reading-content .text-left')
        for bad in contents.select('.lnbad-tag, blockquote'):
            bad.decompose()
        body = self.extract_contents(contents)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
