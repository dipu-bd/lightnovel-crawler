# -*- coding: utf-8 -*-
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://instadoses.com/?s=%s&post_type=wp-manga&op=&author=&artist=&release=&adult='
post_chapter_url = 'https://instadoses.com/wp-admin/admin-ajax.php'


class InstadosesCrawler(Crawler):
    base_url = 'https://instadoses.com/'

    def initialize(self):
        print('inititiaslkaksjdlkasjdlkajsdlkjdls')
        self.executor = ThreadPoolExecutor(max_workers=7)
    # end def

    # NOTE: Site search doesn't work. So this won't work.
    # def search_novel(self, query):
    #     query = query.lower().replace(' ', '+')
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for tab in soup.select('.c-tabs-item__content'):
    #         a = tab.select_one('.post-title h3 a')
    #         latest = tab.select_one('.latest-chap .chapter a').text
    #         votes = tab.select_one('.rating .total_votes').text
    #         results.append({
    #             'title': a.text.strip(),
    #             'url': self.absolute_url(a['href']),
    #             'info': '%s | Rating: %s' % (latest, votes),
    #         })
    #     # end for

    #     return results
    # # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = ' '.join([
            str(x)
            for x in soup.select_one('.post-title h1').contents
            if not x.name
        ]).strip()
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('.summary_image img')['data-src'])
        except Exception:
            pass
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select('.author-content a')
        if len(author) == 2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        else:
            self.novel_author = author[0].text
        logger.info('Novel author: %s', self.novel_author)

        self.novel_id = soup.select_one(
            '.wp-manga-action-button[data-action=bookmark]')['data-post']
        logger.info('Novel id: %s', self.novel_id)

        for span in soup.select('.page-content-listing span'):
            span.decompose()

        logger.info('Sending post request to %s', post_chapter_url)
        response = self.submit_form(post_chapter_url, data={
            'action': 'manga_get_chapters',
            'manga': int(self.novel_id)
        })
        soup = self.make_soup(response)
        for a in reversed(soup.select('.wp-manga-chapter > a')):
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url':  self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select('div.reading-content p')

        body = []
        for p in contents:
            for ad in p.select('h3, .code-block, .adsense-code'):
                ad.decompose()
            body.append(str(p))

        return ''.join(body)
    # end def
# end class
