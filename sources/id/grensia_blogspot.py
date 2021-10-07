# -*- coding: utf-8 -*-
import re
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class GreensiaCrawler(Crawler):
    base_url = 'https://grensia.blogspot.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        soup = self.get_soup(self.novel_url)
        self.novel_title = soup.select_one('meta[property="og:title"]')['content']
        self.novel_cover = soup.select_one('meta[property="og:image"]')['content']

        vols = set([])
        for a in soup.select('.blog-post .post-body a'):
            if not a.has_attr('href') or not a.text.strip():
                continue
            if not re.match(self.base_url + r'\d{4}/\d{2}/.*\.html', a['href']):
                continue

            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            vols.add(vol_id)
            self.chapters.append(dict(
                id=chap_id,
                volume=vol_id,
                title=a.text.strip(),
                url=self.absolute_url(a['href']),
            ))
        # end for

        self.volumes = [dict(id=x) for x in vols]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        soup = self.get_soup(chapter['url'])
        body = soup.select_one('.blog-post .post-body')
        for div in body.select('.entry-header'):
            div.extract()
        return self.extract_contents(body) 
    # end def

# end class
