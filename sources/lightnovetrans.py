# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LNTCrawler(Crawler):
    base_url = 'https://lightnovelstranslations.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)

        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        # TODO: No covers on site, could not grab author name.

        # Extract volume-wise chapter entries
        for div in soup.select('.su-accordion .su-spoiler'):
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
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting: %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        content = soup.select_one('.entry-content')
        for bad in content.select('.alignleft, .alignright, hr, p[style*="text-align: center"]'):
            bad.extract()
        # end for

        return '\n'.join([str(p) for p in content.find_all('p')])

    # end def


# end class
