# -*- coding: utf-8 -*-
import json
import logging
import re
from bs4 import BeautifulSoup
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://mtled-novels.com/search_novel.php?q=%s'
login_url = 'https://mtled-novels.com/login/ajax/checklogin.php'
logout_url = 'https://mtled-novels.com/login/logout.php'


class MtledNovelsCrawler(Crawler):
    base_url = 'https://mtled-novels.com/'

    def login(self, username, password):
        '''login to LNMTL'''
        # Get the login page
        logger.info('Visiting %s', self.home_url)
        self.get_response(self.home_url)

        # Send post request to login
        logger.info('Logging in...')
        response = self.submit_form(
            login_url,
            data=dict(
                myusername=username,
                mypassword=password,
                remember=0,
            ),
        )

        # Check if logged in successfully
        data = response.json()
        logger.debug(data)
        if 'response' in data and data['response'] == 'true':
            print('Logged In')
        else:
            soup = BeautifulSoup(data['response'], 'lxml')
            soup.find('button').extract()
            error = soup.find('div').text.strip()
            raise PermissionError(error)
        # end if
    # end def

    def logout(self):
        '''logout as a good citizen'''
        logger.debug('Logging out...')
        self.get_response(logout_url)
        print('Logged out')
    # end def

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('.card .row .col-lg-2 a')[:5]:
            url = self.absolute_url(a['href'])
            results.append({
                'url': url,
                'title': a.img['alt'],
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.profile__img img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Downloaded from mtled-novels.com"
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.select('div#tab-profile-2 a')

        for a in chapters:
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
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        if soup.h1.text.strip():
            chapter['title'] = soup.h1.text.strip()
        else:
            chapter['title'] = chapter['title']
        # end if

        contents = soup.select('div.translated p')
        for p in contents:
            for span in p.find_all('span'):
                span.unwrap()
            # end for
        # end for
        # self.clean_contents(contents)
        #body = contents.select('p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
