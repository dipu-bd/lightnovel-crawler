# -*- coding: utf-8 -*-
from time import time
import logging
import re
from urllib.parse import urlparse
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_info_url = 'https://www.wattpad.com/v4/parts/%s?fields=id,title,pages,text_url&_=%d'

class WattpadCrawler(Crawler):
    base_url = [
        'https://www.wattpad.com/',
        'https://my.w.tt/',
    ]

    def initialize(self):
        self.home_url = self.base_url[0]

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''

        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select('h1')[0].get_text().strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select('div.cover.cover-lg img')[0]['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select(
            'div.author-info strong a')[0].get_text()
        logger.info('Novel author: %s', self.novel_author)

        #description = soup.select('h2.description')[0].get_text()

        chapters = soup.select('ul.table-of-contents a')
        # chapters.reverse()

        vols = set([])
        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            vols.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        self.volumes = [{'id': i} for i in vols]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        # soup = self.get_soup(chapter['url'])
        # pages = int(re.search(
        #     '[1-9]', re.search('("pages":)([1-9])', str(soup)).group(0)).group(0))
        # #chapter['title'] = soup.select('h2')[0].get_text().strip()
        # contents = []
        # for i in range(1, pages+1):
        #     page_url = chapter['url'] + "/page/" + str(i)
        #     logger.info('Get body text from %s', page_url)
        #     soup_page = self.get_soup(page_url)
        #     for p in soup_page.select('pre p'):
        #         contents.append(p.text)
        # return '<p>' + '</p><p>'.join(contents) + '</p>'

        chapter_id = urlparse(chapter['url']).path.split('-')[0].strip('/')
        info_url = chapter_info_url % (chapter_id, int(time() * 1000))
        
        logger.info('Getting info %s', info_url)
        data = self.get_json(info_url)
        chapter['title'] = data['title']
        
        text_url = data['text_url']['text']
        logger.info('Getting text %s', text_url)
        text = self.get_response(text_url).content.decode('utf-8')
        text = re.sub(r'<p data-p-id="[a-f0-9]+>"', '<p>', text)
        return text
    # end def
# end class
