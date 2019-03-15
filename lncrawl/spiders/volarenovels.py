#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('VOLARE_NOVELS')


class VolareNovelsCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            'header.entry-header h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select('div.entry-content p')[1].text.strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.entry-content img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapter_urls = set([])
        for span in soup.select('.entry-content .collapseomatic'):
            vol_title = span.text.strip()
            vol_id = len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })
            content_id = '#target-%s a' % span['id']
            for a in soup.select(content_id):
                href = self.absolute_url(a['href'])
                self.chapters.append({
                    'id': len(self.chapters) + 1,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': href,
                })
                chapter_urls.add(a['href'])
            # end for
        # end for

        # Add other chapter entries if available
        has_others = False
        vol_id = len(self.volumes) + 1
        for a in soup.select('.entry-content p a'):
            href = self.absolute_url(a['href'])
            if href in chapter_urls or not href.startswith(self.novel_url):
                continue
            # end if
            self.chapters.append({
                'id': len(self.chapters) + 1,
                'volume': vol_id,
                'title': a.text.strip(),
                'url': href,
            })
            has_others = True
        # end for
        if has_others:
            self.volumes.append({
                'id': vol_id,
                'title': '',
            })
        # end if

        logger.debug(self.volumes)
        logger.debug(self.chapters)
        logger.debug('%d volumes and %d chapters found',
                     len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting: %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        embedded_content = soup.select_one(
            '.entry-content blockquote.wp-embedded-content a')
        if embedded_content:
            embed_url = embedded_content['href']
            logger.info('Visiting more: %s', embed_url)
            soup = self.get_soup(embed_url)
        # end if

        content = soup.select_one('.entry-content')
        self.clean_contents(content)
        body = content.select('p')
        body = [str(p) for p in body if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
