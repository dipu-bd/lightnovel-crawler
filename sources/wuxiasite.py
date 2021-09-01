# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://wuxiaworld.site/?s=%s&post_type=wp-manga'


class WuxiaSiteCrawler(Crawler):
    base_url = 'https://wuxiaworld.site/'

    # NOTE: Disabled due to Cloudflare issue.
    # def search_novel(self, query):
    #     query = query.lower().replace(' ', '+')
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for tab in soup.select('.c-tabs-item__content'):
    #         a = tab.select_one('.post-title h4 a')
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
            for x in soup.select_one('.post-title').select_one('h1, h2, h3').contents
            if not x.name
        ]).strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.summary_image a img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select('.author-content a')
        if len(author) == 2:
            self.novel_author = author[0].text + ' (' + author[1].text + ')'
        elif len(author) == 1:
            self.novel_author = author[0].text
        logger.info('Novel author: %s', self.novel_author)

        self.novel_id = soup.select_one('#manga-chapters-holder')['data-id']
        logger.info('Novel Id = %s', self.novel_id)

        soup = self.make_soup(self.submit_form(
            'https://wuxiaworld.site/wp-admin/admin-ajax.php',
            data={
                'action': 'manga_get_chapters',
                'manga': self.novel_id
            }
        ))

        chapters = soup.select('ul.main li.wp-manga-chapter a')
        chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('.text-left, .cha-words, .reading-content')
        return self.extract_contents(content)
    # end def
# end class
