# -*- coding: utf-8 -*-
import logging
from math import ceil
from urllib.parse import quote

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.scribblehub.com/?s=%s&post_type=fictionposts'
chapter_post_url = 'https://www.scribblehub.com/wp-admin/admin-ajax.php'

class ScribbleHubCrawler(Crawler):
    base_url = 'https://www.scribblehub.com/'

    def search_novel(self, query):
        url = search_url % quote(query.lower())
        soup = self.get_soup(url)

        results = []
        for novel in soup.select('div.search_body'):
            a = novel.select_one('.search_title a')
            info = novel.select_one('.search_stats')
            if not isinstance(a, Tag):
                continue
            # end if
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': info.text.strip() if isinstance(info, Tag) else '',
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.find('div', {'class': 'fic_title'})
        assert isinstance(possible_title, Tag)
        self.novel_title = str(possible_title['title']).strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.find('div', {'class': 'fic_image'})
        if isinstance(possible_image, Tag):
            possible_image = possible_image.find('img')
            if isinstance(possible_image, Tag):
                self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        possible_author = soup.find('span', {'class': 'auth_name_fic'})
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info('Novel author: %s', self.novel_author)

        chapter_count = soup.find('span', {'class': 'cnt_toc'})
        chapter_count = int(chapter_count.text) if isinstance(chapter_count, Tag) else -1
        page_count = ceil(chapter_count / 15.0)
        logger.info('Chapter list pages: %d' % page_count)

        possible_mypostid = soup.select_one('input#mypostid')
        assert isinstance(possible_mypostid, Tag)
        mypostid = int(str(possible_mypostid['value']))
        logger.info('#mypostid = %d', mypostid)
        
        possible_chpcounter = soup.select_one('input#chpcounter')
        assert isinstance(possible_chpcounter, Tag)
        chpcounter = int(str(possible_chpcounter['value']))
        logger.info('#chpcounter = %d', chpcounter)

        toc_show = 50
        page_count = ceil(chpcounter / toc_show)
        logger.info('#page count = %d', page_count)

        futures_to_check = []
        for i in range(page_count):
            future = self.executor.submit(self.submit_form, chapter_post_url, {
                'action': 'wi_getreleases_pagination',
                'pagenum': page_count - i,
                'mypostid': mypostid,
            }, headers={
                'cookie': 'toc_show=' + str(toc_show),
            })
            futures_to_check.append(future)
        # end for

        volumes = set()
        for f in futures_to_check:
            response = f.result()
            soup = self.make_soup(response)
            for chapter in reversed(soup.select('.toc_ol a.toc_a')):
                chap_id = len(self.chapters) + 1
                vol_id = len(self.chapters) // 100 + 1
                volumes.add(vol_id)
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'url': self.absolute_url(str(chapter['href'])),
                    'title': chapter.text.strip() or ('Chapter %d' % chap_id),
                })
            # end for
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def initialize(self) -> None:
        self.cleaner.bad_css.update([
            '.modern-footnotes-footnote',
            '.modern-footnotes-footnote__note',
        ])
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('div#chp_raw')
        return self.cleaner.extract_contents(contents)
    # end def
# end class
