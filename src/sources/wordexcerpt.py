# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('WORDEXCERPT')
search_url = 'https://wordexcerpt.com/?s=%s&post_type=wp-manga'


class WordExcerptCrawler(Crawler):
    base_url = 'https://wordexcerpt.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.post-title h1, .c-manga-title h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_img = soup.select_one('.summary_image img')
        if possible_img:
            if possible_img.has_attr('data-src'):
                self.novel_cover = self.absolute_url(possible_img['data-src'])
            if possible_img.has_attr('src'):
                self.novel_cover = self.absolute_url(possible_img['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        possible_author = soup.select_one('.author-content a, .profile-manga a[href*="/author/"]')
        if possible_author:
            self.novel_author = possible_author.text
        logger.info('Novel author: %s', self.novel_author)

        if soup.select('ul.sub-chap'):
            volume_list = soup.select('ul.main li.parent')
            last_vol = -1
            volume = {'id': 0, 'title': 'Volume 1', }
            for item in volume_list:
                vol = volume.copy()
                vol['id'] += 1
                vol_title = 'Volume ' + str(vol['id'])
                volume = vol
                chapter_list = item.select('li.wp-manga-chapter a')
                chapter_list.reverse()
                for chapter in chapter_list:
                    chap_id = len(self.chapters) + 1
                    self.chapters.append({
                        'id': chap_id,
                        'volume': volume['id'],
                        'url':  chapter['href'],
                        'title': chapter.text.strip(),
                    })
                    if last_vol != volume['id']:
                        last_vol = volume['id']
                        self.volumes.append(volume)
                # end for
            # end for
        else:
            chapter_list = soup.select('li.wp-manga-chapter a')
            chapter_list.reverse()
            for chapter in chapter_list:
                chap_id = len(self.chapters) + 1
                if len(self.chapters) % 100 == 0:
                    vol_id = chap_id//100 + 1
                    vol_title = 'Volume ' + str(vol_id)
                    self.volumes.append({
                        'id': vol_id,
                        'title': vol_title,
                    })
                # end if
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'url':  chapter['href'],
                    'title': chapter.text.strip(),
                })
            # end for
        # end if
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        # logger.debug(soup.title.string)
        contents = soup.select('div.text-left p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
