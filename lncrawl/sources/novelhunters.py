# -*- coding: utf-8 -*-
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.novelhunters.com/?s=%s&post_type=wp-manga&op=&author=&artist=&release=&adult='
post_chapter_url = 'https://www.novelhunters.com/wp-admin/admin-ajax.php'


class NovelHunters(Crawler):
    base_url = 'https://www.novelhunters.com/'

    def initialize(self):
        self.executor = ThreadPoolExecutor(max_workers=7)
    # end def

    # NOTE: Site search doesn't work. So this won't work.
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content'):
            a = tab.select_one('.post-title h3 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            })
        # end for

        return results
    # end def

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

        self.novel_author = ' '.join([
            a.text.strip()
            for a in soup.select('.author-content a[href*="novel-author"]')
        ])
        logger.info('%s', self.novel_author)

        self.novel_id = soup.select_one(
            '.wp-manga-action-button[data-action=bookmark]')['data-post']
        logger.info('Novel id: %s', self.novel_id)

        for span in soup.select('.page-content-listing span'):
            span.extract()

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

        contents = soup.select_one('div.text-left')

        for bad in contents.select('h3, .code-block, script, .adsbygoogle, .adsense-code, .sharedaddy, a, br'):
            bad.extract()

        for content in contents.select("p"):
            for bad in ["*** Can’t wait until tomorrow to see more? Want to show your support? to read premium additional chapters ahead of time!", "[T/N Note: To Get more Free chapters Quickly Support us on", ". For more and better novels updates. If you have any suggestions, please give it on the comment box or contact us on"]:
                if bad in content.text:
                    content.extract()

        return self.extract_contents(contents)
    # end def
# end class