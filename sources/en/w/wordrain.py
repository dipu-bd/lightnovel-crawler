# -*- coding: utf-8 -*-
import logging
from bs4 import Tag
from concurrent.futures import ThreadPoolExecutor

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://wordrain69.com/?s=%s'
post_chapter_url = 'https://wordrain69.com/wp-admin/admin-ajax.php'


class WordRain(Crawler):
    base_url = 'https://wordrain69.com'

    def initialize(self):
        self.executor = ThreadPoolExecutor(max_workers=7)



    # NOTE: Site search doesn't work. So this won't work.
    """ def search_novel(self, query):
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


        return results
    """

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert isinstance(possible_title, Tag), 'No novel title'
        self.novel_title = possible_title['content']
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image['content']
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = ' '.join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="manga-translator"]')
            ]
        )
        logger.info('%s', self.novel_author)

        self.novel_id = soup.select_one(
            '.wp-manga-action-button[data-action=bookmark]'
        )['data-post']
        logger.info('Novel id: %s', self.novel_id)

        logger.info('Sending post request to %s', post_chapter_url)
        response = self.submit_form(
            post_chapter_url,
            data={'action': 'manga_get_chapters', 'manga': int(self.novel_id)},
        )
        soup = self.make_soup(response)
        for a in reversed(soup.select('.wp-manga-chapter > a')):
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})

            self.chapters.append(
                {
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                }
            )




    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.text-left')

        for bad in contents.select(
            'h3, .code-block, script, .adsbygoogle, .adsense-code, .sharedaddy, a'
        ):
            bad.extract()

        for content in contents.select("p"):
            for bad in [
                "[The translation belongs to Wordrain. Support us by comments, , or buy Miao a coffee (*´ｪ｀*)っ旦~]",
                "1 ko-Fi = extra chapter",
                "[Thanks to everyone who’s reading this on wordrain. This translation belongs to us. (•̀o•́)ง Support us by comments, , or buy Miao a coffee (´ｪ｀)っ旦~]",
                "1 ko-fi= 1 bonus chapter.",
                "[The translation belongs to Wordrain. Support us by comments, , or buy Miao a coffee (*´ｪ｀*)っ~]",
                "1 ko fi = 1 extra chapter",
                "[The translation belongs to Wordrain. Support us by comments, , or buy Miao a coffee (´ｪ｀)っ旦~]",
                "[The translation belongs to Wordrain . Support us by comments, , or buy Miao a coffee (´ｪ｀)っ旦~]",
                "[Thanks to everyone who are reading this on the site wordrain . (•̀o•́)ง Support us by comments, , or buy Miao a coffee (´ｪ｀)っ旦~]",
                "[Thanks to everyone who’s reading this on wordrain . This translation belongs to us. (•̀o•́)ง Support us by comments, , or buy Miao a coffee (´ｪ｀)っ旦~]",
                "[Thanks to everyone who’s reading this on wordrain . This translation belongs to us. ( •̀o•́)ง Support us by comments, , or buy Miao a coffee ( ´ｪ｀)っ旦~]",
            ]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(contents)





