# -*- coding: utf-8 -*-
import re
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

cover_image_url = 'https://cdn.gravitytales.com/images/covers/%s.jpg'
novel_toc_url = 'http://gravitytales.com/novel/%s'
chapter_list_url = 'http://gravitytales.com/novel/%s/chapters'


class GravityTalesCrawler(Crawler):
    base_url = 'http://gravitytales.com/'

    def read_novel_info(self):
        self.novel_id = re.split(r'\/(novel|post)\/', self.novel_url)[2]
        self.novel_id = self.novel_id.split('/')[0]
        logger.info('Novel id: %s' % self.novel_id)

        self.novel_url = novel_toc_url % self.novel_id
        logger.debug('Visiting %s' % self.novel_url)
        soup = self.get_soup(self.novel_url)

        for tag in soup.select('.main-content h3 > *'):
            tag.extract()
        self.novel_title = soup.select_one('.main-content h3').text.strip()
        logger.info('Novel title: %s' % self.novel_title)

        self.novel_cover = cover_image_url % self.novel_id
        logger.info('Novel cover: %s' % self.novel_cover)

        self.novel_author = soup.select_one('.main-content h4').text.strip()
        logger.info(self.novel_author)

        self.get_chapter_list()
    # end def

    def get_chapter_list(self):
        url = chapter_list_url % self.novel_id
        logger.info('Visiting %s' % url)
        soup = self.get_soup(url)

        # For each tabs...
        for a in soup.select('#chaptergroups li a'):
            vol_id = len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': a.text.strip(),
                '_tid': (a['href']),
            })

            # ...get every chapters
            for a in soup.select_one(a['href']).select('table td a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                })
        # end for

    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s' % chapter['url'])
        soup = self.get_soup(chapter['url'])
        body = soup.select_one('#chapterContent')
        for tag in body.contents:
            if hasattr(tag, 'attrs'):
                setattr(tag, 'attrs', {})    # clear attributes
            # end if
        # end for
        return str(body)
    # end def
# end class
