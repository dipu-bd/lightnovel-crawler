# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

clear = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
crypt = "rhbndjzvqkiexcwsfpogytumalVUQXWSAZKBJNTLEDGIRHCPFOMY"

decrypt_table = dict(zip(clear, crypt))


def decrypt_string(crypted_string):
    return ''.join(map(lambda c: decrypt_table.get(c, c),
                       list(crypted_string)))


class SuperNovelCrawler(Crawler):
    base_url = 'https://secondlifetranslations.com/'

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_title = (soup.select_one('meta[property="og:title"]')
                            ['content'])

        possible_cover = soup.select_one('meta[property="og:image"]')
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover['content'])

        logger.info('Novel cover: %s', self.novel_cover)

        novelcontent = soup.select_one(".novelcontent")
        if novelcontent:
            author_strong = novelcontent.find('strong', string='Author: ')
            if author_strong and author_strong.next_sibling:
                self.novel_author = author_strong.next_sibling

        logger.info('Novel author: %s', self.novel_author)

        for a in soup.select('.panel > form > div > div > a'):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({'id': vol_id})

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.entry-content.clr')
        for span in contents.select('span.jmbl'):
            span.string = decrypt_string(span.text)

        return self.cleaner.extract_contents(contents)
