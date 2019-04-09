#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
import json
import urllib.parse
from concurrent import futures
from ..utils.crawler import Crawler
from bs4 import BeautifulSoup

logger = logging.getLogger('COMRADEMAO')
#search_url = 'http://novelfull.com/search?keyword=%s'


class ComrademaoCrawler(Crawler):

    #temp_chapters = []

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find('h4').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(soup.find('div',{'class':'wrap-thumbnail'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find('div',{'class':'author'}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        #page_count = soup.find('span',{'class':'dots'}).findNext('a').text
        #page_count = -1 if not page_count else int(page_count)
        #logger.info('Chapter list pages: %d' % page_count)

        the_url = soup.find("link",{"rel":"shortlink"})['href']
        p_id = urllib.parse.parse_qs(urllib.parse.urlparse(the_url).query)['p'][0]
        js = self.scrapper.post("https://comrademao.com/wp-admin/admin-ajax.php?action=movie_datatables&p2m=%s" % p_id)
        data = js.json()
        
        chapter_count = data['recordsTotal']
        url = "https://comrademao.com/wp-admin/admin-ajax.php?action=movie_datatables&p2m=%s&length=%s" % (p_id,chapter_count) 
        js = self.scrapper.post(url)
        data = js.json()

        logger.info('Getting chapters...')
        chapters = []
        for chapter in data['data']:
            link = BeautifulSoup(chapter[1],'lxml').find('a')
            chapters.append(link)
        # end for

        chapters.reverse()

        for x in chapters:
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
                'url': self.absolute_url(x['href']),
                'title': x.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
        logger.debug(self.volumes)
        logger.info('%d volumes and %d chapters found' % (len(self.volumes), len(self.chapters)))
    # end def

    #def download_chapter_list(self, page, p_id):
    #    '''Download list of chapters and volumes.'''
    #    url = "https://comrademao.com/wp-admin/admin-ajax.php?action=movie_datatables&p2m=%s&draw=%s" % (p_id,page) 
    #    js = self.scrapper.post(url)
    #    data = js.json()
    #    mini_chapters = []
    #    for chapter in data['data']:
    #        link = BeautifulSoup(chapter[1],'lxml').find('a')
    #        mini_chapters.append(link)
    #    logger.debug('Crawling chapters url in page %s' % page)
    #    return mini_chapters
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        logger.debug(soup.title.string)
        
        #if soup.select('div.entry-content div.container div.container a p'):
        #    contents = soup.select('div.entry-content div.container div.container a p')
        #else:
        #    contents = soup.select('div.entry-content div.container a p')
        
        #contents = soup.select('div.entry-content div p')
        #body_parts = []
        #for x in contents:
        #    body_parts.append(x.text)
        
        #return '<p>' + '</p><p>'.join(body_parts) + '</br></p>'
        #contents = soup.select_one('div.entry-content div')
        if soup.find("div", attrs={"readability":True}):
            contents = soup.find("div", attrs={"readability":True})
        else:
            contents = soup.find("article")
        # end if
        for item in contents.findAll('div'):
            item.decompose()
        # end for
        return contents.prettify()
    # end def
# end class
