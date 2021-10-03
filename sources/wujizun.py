# -*- coding: utf-8 -*- 
import logging
from bs4.element import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class Wujizun(Crawler):
    base_url = 'https://wujizun.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title['content']
        logger.info('Novel title: %s', self.novel_title)

        possible_cover = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_cover, Tag):
            self.novel_cover = possible_cover['content']
        logger.info('Novel cover: %s', self.novel_cover)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one('div.entry-content')
        assert isinstance(toc_parts, Tag)
        for notoc in toc_parts.select('.sharedaddy, .ezoic-adpicker-ad, .ezoic-ad-adaptive, .ezoic-ad'):
            notoc.extract()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        for a in soup.select('div.entry-content p a[href*="wujizun.com/2"]'):
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body_parts = soup.select_one('div.entry-content')

        # Remoeves bad text from chapters.
        self.blacklist_patterns += ["Previous Chapter", "Table of Contents", "Next Chapter", "MYSD Patreon:"]
        self.clean_contents(body_parts)

        return str(body_parts)
    # end def
# end class
