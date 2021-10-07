# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://novelsonline.net/search/autocomplete'


class NovelsOnline(Crawler):
    base_url = 'https://novelsonline.net/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.block-title h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('img', {'alt': self.novel_title})['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author_link = soup.select_one("a[href*=author]")
        if author_link:
            self.novel_author = author_link.text.strip().title()
        # end if
        logger.info('Novel author: %s', self.novel_author)

        volume_ids = set()
        for a in soup.select('.chapters .chapter-chs li a'):
            chap_id = len(self.chapters) + 1
            vol_id = (chap_id - 1) // 100 + 1
            volume_ids.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        self.volumes = [{'id': i} for i in volume_ids]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        div = soup.select_one('.chapter-content3')

        bad_selectors = [
            '.trinity-player-iframe-wrapper'
            '.hidden',
            '.ads-title',
            'script',
            'center',
            'interaction',
            'a[href*=remove-ads]',
            'a[target=_blank]',
            'hr',
            'br',
            '#growfoodsmart',
            '.col-md-6'
        ]
        for hidden in div.select(', '.join(bad_selectors)):
            hidden.extract()
        # end for

        body = self.extract_contents(div)
        if re.search(r'c?hapter .?\d+', body[0], re.IGNORECASE):
            title = body[0].replace('<strong>', '').replace(
                '</strong>', '').strip()
            title = ('C' if title.startswith('hapter') else '') + title
            chapter['title'] = title.strip()
            body = body[1:]
        # end if

        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class