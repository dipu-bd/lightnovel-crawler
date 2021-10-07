# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode
import js2py
from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelMaoCrawler(Crawler):
    machine_translation = True
    base_url = [
        'https://novelmao.com/'
    ]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_id = soup.select_one('input[name="id_novel"]')
        assert isinstance(possible_id, Tag)
        novel_id = possible_id['value']
        logger.info('Novel Id = %s', novel_id)

        try:
            possible_script = soup.select_one('script[type="application/ld+json"]')
            assert isinstance(possible_script, Tag)
            script_text = possible_script.get_text()

            data = js2py.eval_js(script_text)
            self.novel_title = data[2]['name']
            self.novel_cover = data[2]['image']
            self.novel_author = data[2]['author']['name']
            logger.info('Novel title = %s', self.novel_title)
            logger.info('Novel cover = %s', self.novel_cover)
            logger.info('Novel author = %s', self.novel_author)
        except Exception as e:
            possible_title = soup.select_one('meta[itemprop="itemReviewed"], meta[property="og:title"]')
            assert isinstance(possible_title, Tag)
            self.novel_title = possible_title['content']
            logger.info('Novel title = %s', self.novel_title)

            possible_cover = soup.select_one('article .kn-img amp-img')
            if isinstance(possible_cover, Tag):
                self.novel_cover = possible_cover['src']
            # end if
            logger.info('Novel cover = %s', self.novel_cover)
        # end try

        current_page = 0
        temp_chapters = []
        has_more_pages = True
        chapter_list_url = self.absolute_url('/wp-admin/admin-ajax.php')
        while has_more_pages:
            params={
                'action': 'mtl_chapter_json',
                'id_novel': novel_id,
                'view_all': 'yes',
                'moreItemsPageIndex': current_page,
                '__amp_source_origin': self.home_url.strip('/'),
            }
            url = chapter_list_url + '?' + urlencode(params)
            logger.info('Getting chapters: %s', url)
            data = self.get_json(url)
            logger.info('Received %d items', len(data['items']))
            has_more_pages = data['hasMorePages'] == 1
            temp_chapters += data['items']
            current_page += 1
        # end for

        for item in reversed(temp_chapters):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if len(self.chapters) % 100 == 0:
                self.volumes.append({ 'id': vol_id})
            # en if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': item['title'],
                'url': item['permalink']
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        paras = soup.select('main article p.indo')
        return ''.join([
            str(p) for p in paras
            if self.filter_para(p.text.strip())
        ])
    # end def

    def filter_para(self, para):
        bad_texts = [
            'novelmao.com, the fastest update to the latest chapter of Respect Students!'
        ]
        for txt in bad_texts:
            if txt in para:
                return False
        return True
    # end def

# end class
