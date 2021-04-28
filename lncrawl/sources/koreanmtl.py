# -*- coding: utf-8 -*-
import logging
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)


class LightNovelsOnl(Crawler):
    base_url = 'https://www.koreanmtl.online/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        # self.novel_title = soup.select_one('h1.entry-title').text.strip()
        self.novel_title = soup.select_one('.post-title.entry-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        volumes = set([])
        for a in soup.select('.post-body.entry-content ul li a'):
            chap_id = 1 + len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select('.post-body.entry-content p')
        return '\n'.join([str(p) for p in contents if p.text.strip()])
    # end def
# end class
