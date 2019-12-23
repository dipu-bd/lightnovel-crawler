#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
from concurrent import futures
from ..utils.crawler import Crawler

logger = logging.getLogger('COMRADEMAO')


class ComrademaoCrawler(Crawler):

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find('h4').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('div', {'class': 'wrap-thumbnail'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find('div', {'class': 'author'}).text
        self.novel_author = re.sub(' & ', ', ', self.novel_author.strip())
        logger.info('Novel author: %s', self.novel_author)

        page_count = soup.find('span', {'class': 'dots'}).findNext('a').text
        page_count = -1 if not page_count else int(page_count)
        logger.info('Chapter list pages: %d' % page_count)

        logger.info('Getting chapters...')
        futures_to_check = {
            self.executor.submit(
                self.download_chapter_list,
                i + 1,
            ): str(i)
            for i in range(page_count)
        }
        temp_chapters = dict()
        for future in futures.as_completed(futures_to_check):
            page = int(futures_to_check[future])
            temp_chapters[page] = future.result()
        # end for

        logger.info('Building sorted chapter list...')
        for page in reversed(sorted(temp_chapters.keys())):
            for chap in reversed(temp_chapters[page]):
                chap['id'] = len(self.chapters) + 1
                chap['volume'] = len(self.chapters) // 100 + 1
                self.chapters.append(chap)
            # end for
        # end for

        self.volumes = [{'id': i + 1}
                        for i in range(1 + len(self.chapters) // 100)]
    # end def

    def download_chapter_list(self, page):
        url = self.novel_url.split('?')[0].strip('/')
        url += '/page/%d' % page
        logger.debug('Getting chapter list: %s', url)
        soup = self.get_soup(url)
        temp_list = []
        for a in soup.select('tbody td a'):
            temp_list.append({
                'url': self.absolute_url(a['href']),
                'title': a.text.strip(),
            })
        # end for
        return temp_list
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        logger.debug(soup.title.string)

        contents = soup.find("div", attrs={"readability": True})
        if not contents:
            contents = soup.find("article")
        # end if
        self.clean_contents(contents)
        for div in contents.findAll('div'):
            div.extract()
        # end for
        return str(contents)
    # end def
# end class
