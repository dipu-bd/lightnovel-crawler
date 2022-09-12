# -*- coding: utf-8 -*-
import logging
from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://reaperscans.com/?s=%s&post_type=wp-manga'


class Reaperscans(Crawler):
    base_url = 'https://reaperscans.com/'
    
    def initialize(self):
        self.cleaner.blacklist_patterns = set([
            "Translator",
            "Proofreader",
            "Reaper Scans",
            "REAPER SCANS",
            "https://dsc.gg/reapercomics",
            "https://discord.gg/MaRegMFhRb",
            "https://discord.gg/reapercomics",
            "h ttps://discord.gg/reapercomic",
            "____",
            "Join our Discord for updates on releases!",
        ])
    # end def

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content'):
            a = tab.select_one('.post-title h3 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append(
                {
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                    'info': '%s | Rating: %s' % (latest, votes),
                }
            )
        # end for

        return results
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.post-title h1')
        assert isinstance(possible_title, Tag)
        for span in possible_title.select('span'):
            span.extract()
        # end for
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('.summary_image a img')
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = ' '.join(
            [a.text.strip() for a in soup.select('.author-content a[href*="author"]')]
        )
        logger.info('%s', self.novel_author)

        chapter_list_url = self.absolute_url('ajax/chapters', self.novel_url)
        soup = self.post_soup(chapter_list_url, headers={'accept': '*/*'})
        for a in reversed(
            soup.select('.wp-manga-chapter:not(.premium-block) a[href*="/chapter"]')
        ):  # This stops it from trying to download locked premium chapters.
            for span in a.findAll('span'):  # Removes time and date from chapter title.
                span.extract()
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({'id': vol_id})
            # end if
            self.chapters.append(
                {
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                }
            )
        # end for

    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('div.text-left')
        return self.cleaner.extract_contents(contents)
    # end def

# end class
