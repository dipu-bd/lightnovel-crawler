# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class DummyNovelsCrawler(Crawler):
    base_url = 'https://dummynovels.com/'

    def initialize(self) -> None:
        self.cleaner.bad_css.update([
            '.code-block'
        ])
    # end def

    def search_novel(self, query: str):
        keywords = set(query.lower().split())

        soup = self.get_soup('%s/novels/' % self.home_url)

        novels = {}
        for a in soup.select('.elementor-post .elementor-post__title a'):
            novels[a.text.strip()] = {
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            }
        # end for

        results = []
        for novel in novels:
            if any(x in keywords for x in novel['title'].lower().split()):
                results.append(novel)
            # end if
        # end for

        return results
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.elementor-heading-title')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('.elementor-image img')
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for div in soup.select('.elementor-text-editor'):
            if div.text.startswith('Author'):
                self.novel_author = div.text.split(':')[-1].strip()
                break
        # end for
        logger.info('Novel author: %s', self.novel_author)

        possible_toc = None
        for tab in soup.select('.elementor-tab-title[aria-controls]'):
            if str(tab.text).find('Table of Contents') > -1:
                possible_toc = soup.select('#' + str(tab['aria-controls']))
                break
        # end for
        assert isinstance(possible_toc, Tag)

        for tab in possible_toc.select('.elementor-accordion-item .elementor-tab-title'):
            possible_contents = possible_toc.select('#' + str(tab['aria-controls']))
            if not isinstance(possible_contents, Tag):
                continue
            # end if

            vol_id = 1 + len(self.volumes)
            vol_title = tab.select_one('.elementor-accordion-title')
            vol_title = vol_title.text if isinstance(vol_title, Tag) else None
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })

            for a in possible_contents.select('a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url':  self.absolute_url(a['href']),
                })
            # end for
        # end for
    # end def 

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.elementor-widget-theme-post-content')
        return self.cleaner.extract_contents(contents)
    # end def
# end class
