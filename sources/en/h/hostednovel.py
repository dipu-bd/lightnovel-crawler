# -*- coding: utf-8 -*-
import logging
import re

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class HostedNovelCom(Crawler):
    base_url = 'https://hostednovel.com/'

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.text-center h1.font-extrabold')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('section[aria-labelledby="novel-details-heading"] img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
            logger.info('Novel cover: %s', self.novel_cover)

        for div in soup.select('section[aria-labelledby="novel-details-heading"] dl div'):
            dt = div.select_one('.dt')
            dd = div.select_one('.dd')
            if dt and dd and dt.text.strip().startswith('Author:'):
                self.novel_author = dd.text.strip()
                break

        logger.info('Novel author: %s', self.novel_author)

        page_re = re.compile(r'page=(\d+)#chapters')
        final_page = max([
            int(page[0])
            for page in [
                page_re.findall(a['href'])
                for a in soup.select('#chapters nav[aria-label="Pagination"] a')
                if a.has_attr('href')
            ] if len(page) == 1
        ])

        futures = []
        raw_novel_url = re.split(r'[?#]', self.novel_url)[0]
        for page in range(final_page):
            page_url = raw_novel_url + f'?page={page + 1}'
            logger.info('Getting chapters from "%s"', page_url)
            f = self.executor.submit(self.get_soup, page_url)
            futures.append(f)

        for f in futures:
            soup = f.result()
            for a in soup.select('#chapters ul[role="list"] li a'):
                chap_id = len(self.chapters) + 1
                vol_id = 1 + len(self.chapters) // 100
                if len(self.volumes) < vol_id:
                    self.volumes.append({'id': vol_id})

                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                })

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('.chapter')
        return self.cleaner.extract_contents(content)
