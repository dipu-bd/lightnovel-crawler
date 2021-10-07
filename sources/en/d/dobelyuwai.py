# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Dobelyuwai(Crawler):
    machine_translation = True
    base_url = 'https://dobelyuwai.wordpress.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('meta[property="og:title"]')['content']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = soup.select_one('meta[property="og:image"]')['content']
        if 'blank.jpg' in self.novel_cover:
            self.novel_cover = None
        logger.info('Novel cover: %s', self.novel_cover)

        # try:
        #     self.novel_author = soup.select_one('div.entry-content > p:nth-child(2)').text.strip()
        # except Exception as e:
        #     logger.warn('Failed to get novel auth. Error: %s', e)
        # logger.info('%s', self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one('div.entry-content')

        for notoc in toc_parts.select('.sharedaddy, .inline-ad-slot, .code-block, script, .adsbygoogle'):
            notoc.extract()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content a[href*="https://dobelyuwai.wordpress.com/2"]')

        for a in chapters:
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
        self.blacklist_patterns += ["Prev", "ToC", "Next"]
        # Fixes images, so they can be downloaded.
        # all_imgs = soup.find_all('img')
        # for img in all_imgs:
        #     if img.has_attr('data-orig-file'):
        #         src_url = img['src']
        #         parent = img.parent
        #         img.extract()
        #         new_tag = soup.new_tag("img", src=src_url)
        #         parent.append(new_tag)

        return self.extract_contents(body_parts)
    # end def
# end class
