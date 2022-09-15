# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LNTCrawler(Crawler):
    base_url = 'https://lightnovelstranslations.com/'

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('h1.entry-title')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text

        possible_cover = soup.select_one('meta[property="og:image"]')
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover['content'])

        for p in soup.select('.entry-content > p'):
            if 'Author' in p.text:
                self.novel_author = p.text.replace('Author:', '').strip()
                break

        for div in soup.select('.entry-content .su-spoiler'):
            vol = div.select_one('.su-spoiler-title').text.strip()
            vol_id = int(vol) if vol.isdigit() else len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': vol,
            })
            for a in div.select('.su-spoiler-content p a'):
                if not a.has_attr('href'):
                    continue
                self.chapters.append({
                    'id': len(self.chapters) + 1,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                })

    def download_chapter_body(self, chapter):
        logger.info('Visiting: %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        content = soup.select_one('.entry-content')
        for bad in content.select('.alignleft, .alignright, hr, p[style*="text-align: center"]'):
            bad.extract()

        return '\n'.join([str(p) for p in content.find_all('p')])
