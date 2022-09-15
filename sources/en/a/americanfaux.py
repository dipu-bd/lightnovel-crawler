# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class AmericanFaux(Crawler):
    base_url = "https://americanfaux.com/"

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('h1.entry-title')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        image = soup.select_one('.post-media img')
        self.novel_cover = self.absolute_url(image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # It's not perfect as it includes translator name aswell.
        for p in soup.select('div.post-excerpt p'):
            possible_author = re.sub(r'[\(\s\n\)]+', ' ', p.text, re.M).strip()
            if possible_author.startswith('Author:'):
                # possible_author = re.sub('Author:', '', possible_author)
                self.novel_author = possible_author.strip()
                break

        
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select('.entry-content a[href*="americanfaux.com/index.php/"]')

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({'id': vol_id})

            self.chapters.append(
                {
                    'id': chap_id,
                    'volume': vol_id,
                    'url': self.absolute_url(a['href']),
                    'title': a.text.strip() or ('Chapter %d' % chap_id),
                }
            )
        

    

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.entry-content')
        return self.cleaner.extract_contents(contents)

    



