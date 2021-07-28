# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlparse
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class CclawTranslations(Crawler):
    base_url = [
        'https://cclawtranslations.home.blog/',
        'https://domentranslations.wordpress.com/',
    ]

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('meta[property="og:title"]')['content']
        #self.novel_title = self.novel_title.rsplit(' ', 1)[0].strip()
        logger.debug('Novel title = %s', self.novel_title)

        self.novel_cover = soup.select_one('meta[property="og:image"]')['content']
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one('meta[property="og:site_name"]')['content']
        logger.info("%s", self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one('div.entry-content')
        for notoc in toc_parts.select('.sharedaddy, .inline-ad-slot, .code-block, script, hr, .adsbygoogle'):
            notoc.extract()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        hostname = urlparse(self.novel_url).hostname or ''
        for a in soup.select('div.entry-content a'):
            if not re.search(hostname + r'/\d{4}/\d{2}/', a['href']):
                continue
            # end if
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url':  self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body_parts = soup.select_one('div.entry-content')
        self.blacklist_patterns += ['CONTENIDO | SIGUIENTE']

        # Fixes images, so they can be downloaded.
        # for img in soup.find_all('img'):
        #     if img.has_attr('data-orig-file'):
        #         src_url = img['src']
        #         parent = img.parent
        #         img.extract()
        #         new_tag = soup.new_tag("img", src=src_url)
        #         parent.append(new_tag)

        return self.extract_contents(body_parts)
    # end def
# end class