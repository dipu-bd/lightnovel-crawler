# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
full_chapter_list_url = 'https://wuxiaworldsite.co/get-full-list.ajax?id=%s'


class WuxiaSiteCo(Crawler):
    base_url = 'https://wuxiaworldsite.co/'

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.read-item h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.read-item .img-read img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select('.read-item .content-reading p')[0].text.strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_id = soup.select_one('.story-introduction__toggler .show-more-list')['data-id']
        logger.info('Novel Id: %s', self.novel_id)

        soup = self.get_soup(full_chapter_list_url % self.novel_id)

        volumes = set([])
        for a in soup.select('a'):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': 'Chapter %d' % chap_id,
                'url': self.absolute_url(a['href']),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        
        contents = soup.select_one('div.content-story')
        for bad in contents.select('p[style="display: none"], script, ins'):
            bad.extract()
        # end for

        return '\n'.join([str(p) for p in contents.select('p') if p.text.strip()])
    # end def
# end class
