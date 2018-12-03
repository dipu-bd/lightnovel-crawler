#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [WebNovel](https://www.webnovel.com).
"""
import json
import logging
import re
from .utils.crawler import Crawler

logger = logging.getLogger('WEBNOVEL')

book_info_url = 'https://www.webnovel.com/book/%s'
chapter_info_url = 'https://www.webnovel.com/book/%s/%s'
book_cover_url = 'https://img.webnovel.com/bookcover/%s/600/600.jpg'
chapter_list_url = 'https://www.webnovel.com/apiajax/chapter/GetChapterList?_csrfToken=%s&bookId=%s'
chapter_body_url = 'https://www.webnovel.com/apiajax/chapter/GetContent?_csrfToken=%s&bookId=%s&chapterId=%s'


class WebnovelCrawler(Crawler):
    @property
    def supports_login(self):
        return False
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def read_novel_info(self):
        logger.info('Getting CSRF Token')
        self.get_response(self.novel_url)
        self.csrf = self.cookies['_csrfToken']
        logger.debug('CSRF Token = %s', self.csrf)

        url = self.novel_url
        self.novel_id = re.search(r'(?<=webnovel.com/book/)\d+', url).group(0)
        logger.debug('Novel Id: %s', self.novel_id)
        url = chapter_list_url % (self.csrf, self.novel_id)
        logger.info('Downloading novel info from %s', url)
        response = self.get_response(url)
        data = response.json()
        logger.debug(data)

        if 'bookInfo' in data['data']:
            self.novel_title = data['data']['bookInfo']['bookName']
            self.novel_cover = book_cover_url % self.novel_id
        # end if

        chapters = []
        if 'volumeItems' in data['data']:
            for vol in data['data']['volumeItems']:
                vol_id = vol['index'] or (len(self.volumes) + 1)
                vol_title = vol['name'].strip() or ('Volume %d' % vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
                for chap in vol['chapterItems']:
                    chap['volume'] = vol_id
                    chapters.append(chap)
                # end if
            # end for
        elif 'chapterItems' in data['data']:
            chapters = data['data']['chapterItems']
            for vol in range(len(chapters) // 100 + 1):
                self.volumes.append({
                    'id': vol,
                    'title': 'Volume %d' % (vol + 1),
                })
            # end for
        # end if
        logger.debug(self.volumes)
        logger.info('%d volumes found', len(self.volumes))

        for i, chap in enumerate(chapters):
            self.chapters.append({
                'id': i + 1,
                'hash': chap['id'],
                'title': chap['name'].strip(),
                'url': chapter_body_url % (self.csrf, self.novel_id, chap['id']),
                'volume': chap['volume'] if 'volume' in chap else (1 + i // 100),
            })
        # end for
        logger.debug(self.chapters)
        logger.info('%d chapters found', len(self.chapters))
    # end def

    def get_chapter_index_of(self, url):
        if not url:
            return 0
        # end if
        url = url.replace('http://', 'https://')
        for chap in self.chapters:
            chap_url = chapter_info_url % (self.novel_id, chap['hash'])
            if url.startswith(chap_url):
                return chap['id']
            # end if
        # end for
        return 0
    # end def

    def download_chapter_body(self, chapter):
        url = chapter['url']
        logger.info('Getting chapter... %s [%s]',
                    chapter['title'], chapter['id'])

        response = self.get_response(url)
        data = response.json()

        if 'authorName' in data['data']['bookInfo']:
            self.novel_author = data['data']['bookInfo']['authorName'] or self.novel_author
        if 'authorItems' in data['data']['bookInfo']:
            self.novel_author = ', '.join([
                x['name'] for x in
                data['data']['bookInfo']['authorItems']
            ]) or self.novel_author
        # end if

        body = data['data']['chapterInfo']['content']
        body = body.replace(r'[ \n\r]+', '\n')
        if ('<p>' not in body) or ('</p>' not in body):
            body = body.replace('<', '&lt;')
            body = body.replace('>', '&gt;')
            body = [x for x in body.split('\n') if len(x.strip())]
            body = '<p>' + '</p><p>'.join(body) + '</p>'
        # end if
        return body.strip()
    # end def
# end class
