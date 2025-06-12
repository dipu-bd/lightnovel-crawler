# -*- coding: utf-8 -*-
import logging
import re

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume, Chapter

logger = logging.getLogger(__name__)


class HostedNovelCom(Crawler):
    base_url = 'https://hostednovel.com/'

    def extract_number_from_string(self, input_string):
        return int(re.findall(r"[-+]?\d*\.\d+|\d+", input_string)[0])

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.text-center h1.font-extrabold')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()

        details = soup.select_one('section[aria-labelledby="novel-details-heading"]')
        if details:
            possible_image = details.select_one('img[src]')
            if possible_image:
                self.novel_cover = self.absolute_url(str(possible_image['src']))

            self.novel_tags = []
            for div in details.select('dl.grid div'):
                dt = div.select_one('dt')
                dd = div.select_one('dd')
                if dt and dd:
                    name = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    if 'author' in name:
                        self.novel_author = value
                    elif 'genres' in name:
                        self.novel_tags.append(value)
                    elif 'status' in name:
                        self.novel_tags.append(value)

        final_pg = 1
        final_pg_el = soup.select_one('#chapters nav[aria-label="Pagination"] a:nth-last-child(1)')
        final_pg_href = final_pg_el and final_pg_el.get("href")
        if final_pg_href:
            final_pg = self.extract_number_from_string(str(final_pg_href))
        logger.info(f'max_page = {final_pg}')

        futures = []
        raw_novel_url = re.split(r'[?#]', self.novel_url)[0]
        for page in range(final_pg):
            page_url = raw_novel_url + f'?page={page + 1}'
            logger.info('Getting chapters from "%s"', page_url)
            f = self.executor.submit(self.get_soup, page_url)
            futures.append(f)

        for f in futures:
            soup = f.result()
            for a in soup.select('#chapters ul[role="list"] li a[href]'):
                chap_id = len(self.chapters) + 1
                vol_id = 1 + len(self.chapters) // 100
                if len(self.volumes) < vol_id:
                    self.volumes.append(Volume(id=vol_id))
                self.chapters.append(Chapter(
                    id=chap_id,
                    volume=vol_id,
                    title=a.text.strip(),
                    url=self.absolute_url(str(a['href'])),
                ))

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('.chapter')
        return self.cleaner.extract_contents(content)
