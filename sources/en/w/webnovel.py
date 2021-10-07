# -*- coding: utf-8 -*-
import logging
import re
import time
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_info_url = 'https://www.webnovel.com/book/%s'
chapter_info_url = 'https://www.webnovel.com/book/%s/%s'
book_cover_url = 'https://img.webnovel.com/bookcover/%s/600/600.jpg?coverUpdateTime=%s&imageMogr2/quality/80'
chapter_list_url = 'https://www.webnovel.com/go/pcm/chapter/get-chapter-list?_csrfToken=%s&bookId=%s&pageIndex=0'
chapter_body_url = 'https://www.webnovel.com/go/pcm/chapter/getContent?_csrfToken=%s&bookId=%s&chapterId=%s'
search_url = 'https://www.webnovel.com/go/pcm/search/result?_csrfToken=%s&pageIndex=1&type=1&keywords=%s'


class WebnovelCrawler(Crawler):
    base_url = [
        'https://m.webnovel.com',
        'https://www.webnovel.com',
    ]

    def get_csrf(self):
        logger.info('Getting CSRF Token')
        self.get_response(self.home_url)
        self.csrf = self.cookies['_csrfToken']
        logger.debug('CSRF Token = %s', self.csrf)
    # end def

    def search_novel(self, query):
        self.get_csrf()
        query = quote_plus(str(query).lower())
        data = self.get_json(search_url % (self.csrf, query))

        results = []
        for book in data['data']['bookInfo']['bookItems']:
            results.append({
                'title': book['bookName'],
                'url': book_info_url % book['bookId'],
                'info': '%(categoryName)s | Score: %(totalScore)s' % book,
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        self.get_csrf()
        url = self.novel_url
        #self.novel_id = re.search(r'(?<=webnovel.com/book/)\d+', url).group(0)
        if not "_" in url:
            self.novel_id = re.search(r'(?<=webnovel.com/book/)\d+', url).group(0)
        else:
            self.novel_id = url.split("_")[1]
        logger.info('Novel Id: %s', self.novel_id)

        url = chapter_list_url % (self.csrf, self.novel_id)
        logger.info('Downloading novel info from %s', url)
        response = self.get_response(url)
        data = response.json()['data']

        if 'bookInfo' in data:
            logger.debug('book info: %s', data['bookInfo'])
            self.novel_title = data['bookInfo']['bookName']
            self.novel_cover = book_cover_url % (self.novel_id, int(1000 * time.time()))
        # end if

        chapterItems = []
        if 'volumeItems' in data:
            logger.debug('volume items: %d', len(data['volumeItems']))
            for vol in data['volumeItems']:
                vol_id = len(self.volumes) + 1
                self.volumes.append({
                    'id': vol_id,
                    'title': vol['volumeName'].strip(),
                })
                for chap in vol['chapterItems']:
                    chap['volume'] = vol_id
                    chapterItems.append(chap)
                # end if
            # end for
        elif 'chapterItems' in data:
            logger.debug('chapter items: %d', len(data['chapterItems']))
            chapterItems = data['chapterItems']
            self.volumes = [{ 'id': x} for x in range(len(chapterItems) // 100 + 1)]
        # end if

        for i, chap in enumerate(chapterItems):
            if chap['isVip'] > 0:
                continue
            # end if
            self.chapters.append({
                'id': i + 1,
                'hash': chap['chapterId'],
                'title': 'Chapter %s: %s' % (chap['chapterIndex'], chap['chapterName'].strip()),
                'url': chapter_body_url % (self.csrf, self.novel_id, chap['chapterId']),
                'volume': chap['volume'] if 'volume' in chap else (1 + i // 100),
            })
        # end for
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
        logger.info('Getting chapter... %s [%s]', chapter['title'], chapter['id'])

        response = self.get_response(url)
        data = response.json()['data']

        if 'authorName' in data['bookInfo']:
            self.novel_author = data['bookInfo']['authorName'] or self.novel_author
        if 'authorItems' in data['bookInfo']:
            self.novel_author = ', '.join([
                x['name'] for x in
                data['bookInfo']['authorItems']
            ]) or self.novel_author
        # end if

        chapter_info = data['chapterInfo']
        if 'content' in chapter_info:
            body = chapter_info['content']
            body = re.sub(r'[\n\r]+', '\n', body)
            return self.format_text(body)
        elif 'contents' in chapter_info:
            body = [
                re.sub(r'[\n\r]+', '\n', x['content'])
                for x in chapter_info['contents']
                if x['content'].strip()
            ]
            return self.format_text('\n'.join(body))
        # end if

        return None
    # end def

    def format_text(self, text):
        text = re.sub(r'Find authorized novels in Webnovel(.*)for visiting\.',
                      '', text, re.MULTILINE)
        text = re.sub(r'\<pirate\>(.*?)\<\/pirate\>', '', text, re.MULTILINE)
        if not (('<p>' in text) and ('</p>' in text)):
            text = re.sub(r'<', '&lt;', text)
            text = re.sub(r'>', '&gt;', text)
            text = [x.strip() for x in text.split('\n') if x.strip()]
            text = '<p>' + '</p><p>'.join(text) + '</p>'
        # end if
        return text.strip()
    # end def
# end class
