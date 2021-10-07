# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import parse_qsl, urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_details_url = 'https://tiknovel.com/book/ajaxchap'


class TikNovelCrawler(Crawler):
    base_url = [
        'http://tiknovel.com/',
        'https://tiknovel.com/',
    ]

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            '#content .detail-wrap h1.detail-tit').text
        logger.info('Novel title: %s', self.novel_title)

        possible_authors = soup.select('#content table.detail-profile td')
        for td in possible_authors:
            if '作者' in td.find('strong').text:
                td.find('strong').extract()
                self.novel_author = td.text.strip()
                break
            # end if
        # end for
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('#content .detail-thumb-box img')['data-echo'])
        logger.info('Novel cover: %s', self.novel_cover)

        volumes = set()
        for a in soup.select('#content .contents-lst li a'):
            ch_id = int(a.find('span').text.strip())
            vol_id = 1 + (ch_id - 1) // 100
            volumes.add(vol_id)
            self.chapters.append({
                'id': ch_id,
                'volume': vol_id,
                'title': a['title'],
                'url':  self.absolute_url(a['href']),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        query_str = urlparse(chapter['url']).query
        data_params = {x[0]: int(x[1]) for x in parse_qsl(query_str)}
        logger.debug("Requesting body with: %s", data_params)
        response = self.submit_form(chapter_details_url, data=data_params)
        data = response.json()
        chap_desc = data['data']['chap']['desc']
        chap_desc = re.sub(r'((<br\/>)|\n)+', '\n\n', chap_desc, flags=re.I)
        contents = chap_desc.split('\n\n')
        contents = [p for p in contents if p and p.strip()]
        return '<p>' + '</p><p>'.join(contents) + '</p>'
    # end def
# end class
