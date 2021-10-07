# -*- coding: utf-8 -*-
import logging
import re

from bs4 import BeautifulSoup

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_url = 'https://www.rebirth.online/novel/%s'


class RebirthOnlineCrawler(Crawler):
    base_url = 'https://www.rebirth.online/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        self.novel_id = self.novel_url.split(
            'rebirth.online/novel/')[1].split('/')[0]
        logger.info('Novel Id: %s', self.novel_id)

        self.novel_url = book_url % self.novel_id
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h2.entry-title a').text
        logger.info('Novel title: %s', self.novel_title)

        translator = soup.find(
            'h3', {'class': 'section-title'}).findNext('p').text
        author = soup.find('h3', {'class': 'section-title'}
                           ).findNext('p').findNext('p').text
        self.novel_author = 'Author : %s, Translator: %s' % (
            author, translator)
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = None
        logger.info('Novel cover: %s', self.novel_cover)

        last_vol = -1
        volume = {'id': 0, 'title': 'Volume 1', }
        for item in soup.find('div', {'class': 'table_of_content'}).findAll('ul'):
            vol = volume.copy()
            vol['id'] += 1
            vol['title'] = 'Book %s' % vol['id']
            volume = vol
            self.volumes.append(volume)
            for li in item.findAll('li'):
                chap_id = len(self.chapters) + 1
                a = li.select_one('a')
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol['id'],
                    'url': self.absolute_url(a['href']),
                    'title': a.text.strip() or ('Chapter %d' % chap_id),
                })
                # end if
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        if len(soup.findAll('br')) > 10:
            contents = soup.find('br').parent
        else:
            remove = ['http://www.rebirth.online', 'support Content Creators', 'content-copying bots',
                      'Firefox Reader\'s Mode', 'content-stealing websites', 'rebirthonlineworld@gmail.com',
                      'PayPal or Patreon', 'available for Patreons', 'Join us on Discord', 'enjoy this novel']
            contents = soup.find('div', {'class': 'obstruction'}).select('p')
            for content in contents:
                for item in remove:
                    if item in content.text:
                        content.extract()
                    # end if
                # end for
            # end for
            tmp = ''
            for content in contents:
                tmp = tmp + '<p>' + content.text + '</p>'
                contents = BeautifulSoup(tmp, 'lxml')
            # end for
        # end if

        return str(contents)
    # end def
# end class
