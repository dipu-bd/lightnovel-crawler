# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class LazyGirlTranslationsCrawler(Crawler):
    base_url = 'https://lazygirltranslations.com/'

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.entry-title').text.strip()
        
        cover_img = soup.select_one('.entry-content .wp-block-image img')      
        if cover_img:
            self.novel_cover = self.absolute_url(cover_img['data-ezsrc'])
        # end if

        first_p = soup.select_one("div.entry-content p")

        for text in first_p.get_text(separator='\n', strip=True).split('\n'):
            if text.startswith('Author'):
                self.novel_author = text.replace("Author: ", "")
                break
            # end if
        # end for

        for a in soup.select('.wp-block-column a'):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip(),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select('.entry-content p')
        for index, p in enumerate(contents):
            a = p.select_one(f'a[href="{self.novel_url}"]')
            if a and a.text == 'Table of Contents':
                contents = contents[index + 1:-1]
                break
            # end if
        # end for
        return ''.join([str(p) for p in contents])
    # end def
# end class