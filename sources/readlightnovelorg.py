# -*- coding: utf-8 -*-
import logging
from bs4.element import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.readlightnovel.org/search/autocomplete'


class ReadLightNovelCrawler(Crawler):
    base_url = [
        'https://readlightnovel.org/',
        'https://www.readlightnovel.org/',
        'https://readlightnovel.me/',
        'https://www.readlightnovel.me/',
    ]

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.block-title h1')
        assert isinstance(possible_title, Tag), 'Novel title is not found'
        self.novel_title = possible_title.text
        logger.info('Novel title: %s', self.novel_title)

        possible_cover = soup.find('img', {'alt': self.novel_title})
        if isinstance(possible_cover, Tag):
            self.novel_cover = self.absolute_url(possible_cover['src'])
        # end if
        logger.info('Novel cover: %s', self.novel_cover)
        
        author_link = soup.select_one("a[href*=author]")
        if isinstance(author_link, Tag):
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

        div = soup.select_one('.chapter-content3 .desc')
        assert isinstance(div, Tag)

        possible_title = div.select_one('h3')
        if isinstance(possible_title, Tag):
            chapter['title'] = possible_title.text.strip()
        # end if

        self.bad_css += [
            'h3',
            '.trinity-player-iframe-wrapper'
            '.hidden',
            '.ads-title',
            'center',
            'interaction',
            'p.hid',
            'a[href*=remove-ads]',
            'a[target=_blank]',
            '#growfoodsmart',
            '#chapterhidden',
            'div[style*="float:left;margin-top:15px;"]',
            'div[style*="float: left; margin-top: 20px;"]',
        ]

        return self.extract_contents(div)
    # end def
# end class
