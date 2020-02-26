# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('ROYALROAD')
search_url = 'https://www.royalroad.com/fictions/search?keyword=%s'


class RoyalRoadCrawler(Crawler):
    base_url = 'https://www.royalroad.com/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('h2.fiction-title a')[:5]:
            url = self.absolute_url(a['href'])
            results.append({
                'url': url,
                'title': a.text.strip(),
                'info': self.search_novel_info(url),
            })
        # end for

        return results
    # end def

    def search_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        score = soup.select_one('span.star')['data-content']
        chapters = len(soup.find('tbody').findAll('a', href=True))
        latest = soup.find('tbody').findAll('a', href=True)[-1].text.strip()
        info = 'Score: %s, Chapter count %s, Latest: %s' % (
            score, chapters, latest)

        return info
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"property": "name"}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find("img", {"class": "img-offset thumbnail inline-block"})['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find(
            "h4", {"property": "author"}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find('tbody').findAll('a', href=True)

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
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)

        if 'Chapter' in soup.select_one('h2').text:
            chapter['title'] = soup.select_one('h2').text
        else:
            chapter['title'] = chapter['title']
        # end if

        contents = soup.find("div", {"class": "chapter-content"})

        self.clean_contents(contents)
        return str(contents)
    # end def
# end class
