# -*- coding: utf-8 -*-

import re
from typing import List
import js2py
from lncrawl.app.models import *
from lncrawl.app.scraper import Scraper, Context

LOGIN_URL = 'https://lnmtl.com/auth/login'
LOGOUT_URL = 'https://lnmtl.com/auth/logout'


class LNMTLScraper(Scraper):
    base_urls = ['https://lnmtl.com/']

    def login(self, ctx: Context) -> bool:
        soup = self.get_sync(LOGIN_URL).soup
        if soup.find('a', {'href': LOGOUT_URL}):
            return True

        token = soup.select_value('form input[name="_token"]', value_of='value')
        self.log.debug('Login token: %s', token)
        response = self.post_sync(LOGIN_URL, body={
            '_token': token,
            'email': ctx.login_id,
            'password': ctx.login_password,
        })

        soup = response.soup
        if not soup.find('a', {'href': LOGOUT_URL}):
            error = soup.select_value('.has-error .help-block', value_of='text')
            raise Exception(error or 'Failed to login')
        return True

    def fetch_info(self, ctx: Context) -> None:
        soup = self.get_sync(ctx.toc_url).soup

        # Parse novel
        ctx.novel.language = Language.ENGLISH
        ctx.novel.name = soup.select_value('.novel .media .novel-name', value_of='text')
        ctx.novel.cover_url = soup.select_value('.novel .media img', value_of='src')
        ctx.novel.details = str(soup.select_one('.novel .media .description')).strip()

        ctx.novel.name = re.sub('[^\u0000-\u00FF]', '', ctx.novel.name)

        # Find authors
        for dl in soup.select('.panel-default .panel-body dl'):
            key = dl.find('dt').text
            if key == 'Authors':
                value = dl.find('dd').text
                author = Author(value, AuthorType.AUTHOR)
                ctx.authors.add(author)

        # Parse volumes
        script = soup.find(name='main').find_next_sibling(name='script').string
        data = js2py.eval_js("window = {}; lnmtl = {};" + script + "; lnmtl;").to_dict()

        future_chapters = []
        for i, item in enumerate(data['volumes']):
            serial = item.get('number', i)
            vol = ctx.add_volume(serial)
            vol.name = item.get('title', '') or ''
            vol.extra.update(item)

        # Parse chapters

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        raise NotImplementedError()
