# -*- coding: utf-8 -*-
import logging
from ..utils.crawler import Crawler

logger = logging.getLogger('NOVELCOOL')

class NovelCool(Crawler):
    base_url = 'https://www.novelcool.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        soup = self.get_soup(self.novel_url)
        self.novel_title = soup.select_one('h1.bookinfo-title').text.strip()
        self.novel_author = soup.select_one('span', {'itemprop': 'creator'}).text.strip()
        logger.info(self.novel_author)
        self.novel_cover = self.absolute_url(
            soup.select_one('div.bookinfo-pic img')['src'])

        chapters = soup.select('.chapter-item-list a')
        chapters.reverse()

        for x in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': self.absolute_url(x['href']),
                'title': x.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        # TODO: Find a way to clean Chapter title, as it giving duplicates.
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.chapter-reading-section')
        body = self.extract_contents(contents)
        return '<p>' + '</p><p>'.join(body) + '</p'
    # end def
# end class