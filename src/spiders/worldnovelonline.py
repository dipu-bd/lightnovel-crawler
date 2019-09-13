#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [worldnovel.online](https://www.worldnovel.online/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler
import urllib.parse
from operator import itemgetter, attrgetter

logger = logging.getLogger('WORLDNOVEL_ONLINE')
search_url = 'https://www.worldnovel.online/?s=%s'
#chapter_list_url = 'https://www.worldnovel.online/wp-json/writerist/v1/chapters?category=%s'
chapter_list_url = "https://www.worldnovel.online/wp-json/writerist/v1/chapters?category=%s&perpage=4000&order=ASC&paged=1"

class WorldnovelonlineCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('article div h3 a')[:5]:
            url = self.absolute_url(a['href'])
            results.append({
                'url': url,
                'title': self.trim_search_title(a.text.strip()),
            })
        # end for

        return results
    # end def

    def trim_search_title(self, title):
        '''Trim title search result'''
        removal_list = ['Novel', 'Bahasa', 'Indonesia','WorldNovel','–','READ']
        edit_string_as_list = title.split()
        final_list = [
            word for word in edit_string_as_list
            if word not in removal_list
        ]
        final_string = ' '.join(final_list)
        return final_string

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        #self.novel_title = self.trim_search_title(soup.title.string)
        self.novel_title = soup.select_one(
            'h1.elementor-heading-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        #self.novel_cover = soup.find('div', {'class': 'row'}).find('img')['src']
        self.novel_cover = self.absolute_url(
            soup.find('div', {'class': 'elementor-image'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)
 
        self.novel_author = soup.find('div',{'class':'lightnovel-info'}).findAll('p')[4].find('a').text
        logger.info('Novel author: %s', self.novel_author)

        path = urllib.parse.urlsplit(self.novel_url)[2]
        book_id = path.split('/')[2]
        list_url = chapter_list_url % (book_id)
        logger.debug('Visiting %s', list_url)
        data = self.get_json(list_url)
        print(data['code'])
        
        if data['code']=='rest_no_route' :

            chapters = soup.select('div.lightnovel-episode ul li a')
            temp_chapters = []
            descending = False
            for a in chapters:
                if 'book' in a.text.strip().lower():
                    chap_id = len(temp_chapters) + 1
                    descending = True
                else:
                    try:
                        chap_id = int(re.findall(
                            r'\d+', a.text.lower().split('chapter', 1)[1])[0])
                    except:
                        chap_id = len(temp_chapters) + 1
                        descending = True
                    # end try
                # end if
                temp_chapters.append({
                    'id': chap_id,
                    'url': a['href'],
                    'title': a.text.strip(),
                })
            # end for

            if descending:
                temp_chapters.reverse()
            else:
                temp_chapters.sort(key=itemgetter('id'))
            # end if

            for a in temp_chapters:
                chap_id = len(self.chapters) + 1
                if len(self.chapters) % 100 == 0:
                    vol_id = (chap_id - 1) // 100 + 1
                    vol_title = 'Volume ' + str(vol_id)
                    self.volumes.append({
                        'id': vol_id,
                        'title': vol_title,
                    })
                # end if
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'url':  self.absolute_url(a['url']),
                    'title': a['title'],
                })
            # end for
        else : 
            data.reverse()
            for item in data:
                self.chapters.append({
                    'id': len(self.chapters) + 1,
                    'volume': len(self.chapters)//100 + 1,
                    'title': item['post_title'],
                    'url': item['permalink'],
                })
            # end for

            self.volumes = [
                {'id': x + 1}
                for x in range(len(self.chapters) // 100 + 1)
            ]
        # end if

        # logger.debug(self.chapters)
        logger.debug('%d volumes and %d chapters found',
                     len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)
        if soup.select_one('div.post-content'):
            contents = soup.select_one('div.post-content') 
        else: 
            contents = soup.select_one('div#chapter-content')
        #if contents is None:
        #    contents = '<p>Something Wrong Happened</p>'
        for block in contents.select('div.code-block'):
            block.decompose()
        for nav in contents.select('div.wp-post-navigation'):
            nav.decompose()
        if contents.em:
            contents.em.decompose()
        return contents.prettify()
    # end def
# end class
