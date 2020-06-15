# -*- coding: utf-8 -*-

from typing import List

from ..app.models import *
from ..app.scraper.scraper import Scraper

LOGIN_URL = 'https://lnmtl.com/auth/login'
LOGOUT_URL = 'https://lnmtl.com/auth/logout'


class LNMTLScraper(Scraper):
    base_urls = ['https://lnmtl.com/']

    def login(self, email: str, password: str) -> bool:
        soup = self.get_sync(LOGIN_URL).soup
        token = soup.select_value('form input[name="_token"]', value_of='value')
        self.log.debug('Login token: %s', token)

        soup = self.post_sync(LOGIN_URL, body={
            '_token': token,
            'email': email,
            'password': password,
        }).soup

        if not soup.find('a', {'href': LOGOUT_URL}):
            error = soup.select_value('.has-error .help-block', value_of='text')
            raise Exception(error or 'Failed to login')

        return True

    def fetch_novel_info(self, url: str) -> Novel:
        soup = self.get_sync(url).soup

        # Parse novel
        novel = Novel(url)
        novel.language = Language.ENGLISH
        novel.name = soup.select_value('.novel .media .novel-name', value_of='text')
        novel.cover_url = soup.select_value('.novel .media img', value_of='src')
        novel.details = str(soup.select_one('.novel .media .description')).strip()

        # Find authors
        for dl in soup.select('.panel-default .panel-body dl'):
            key = dl.find('dt').text
            if key == 'Authors':
                value = dl.find('dd').text
                novel.authors.append(Author(value, author_type=AuthorType.AUTHOR))

        # Parse volumes
        # Parse chapters

        return novel

    def fetch_chapter_content(self, chapter: Chapter) -> Chapter:
        raise NotImplementedError()
