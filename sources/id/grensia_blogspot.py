# -*- coding: utf-8 -*-
import json
import logging
import re

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


novel_info_url = '/feeds/posts/default/-/%s?&orderby=published&alt=json-in-script&callback=startpost2&max-results=99999'

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')


def camel_to_title(s):
    s = _underscorer1.sub(r'\1_\2', s)
    s = _underscorer2.sub(r'\1_\2', s).lower()
    return ' '.join([x.title() for x in s.split('_')])


class GreensiaCrawler(Crawler):
    base_url = 'https://grensia.blogspot.com/'

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(['h1'])

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_image = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_image, Tag):
            self.novel_cover = possible_image['content']
        logger.info('Novel cover: %s', self.novel_cover)

        response = None

        script_tag = soup.select_one('script[src^="/feeds/posts/default/-/"]')
        if isinstance(script_tag, Tag):
            response = self.get_response(self.absolute_url(script_tag['src']))

        a_search = soup.select_one('#breadcrumb a[href*="/search/label/"], #main span.search-label')
        if not response and isinstance(a_search, Tag):
            response = self.get_response(self.absolute_url(novel_info_url % a_search.text.strip()))

        if not response:
            raise Exception('Please enter a valid novel page link')

        data = json.loads(re.findall(r'startpost2\((.*)\);', response.text)[0])

        possible_title = re.findall(r'/posts/default/-/([^/?]+)', response.url)[0]
        self.novel_title = camel_to_title(possible_title)
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_author = str(data['feed']['author'][0]['name']['$t']).title()
            logger.info('Novel author: %s', self.novel_author)
        except Exception:
            pass

        vols = set([])
        for entry in reversed(data['feed']['entry']):
            a_href = None
            for link in entry['link']:
                if link['rel'] == 'alternate':
                    a_href = link['href']
            if not a_href:
                continue

            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            vols.add(vol_id)

            self.chapters.append(dict(
                id=chap_id,
                volume=vol_id,
                title=entry['title']['$t'],
                url=self.absolute_url(a_href),
            ))

        self.volumes = [dict(id=x) for x in vols]

    def download_chapter_body(self, chapter):
        logger.debug('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        body = soup.select_one('.post-body')
        assert isinstance(body, Tag)
        return self.cleaner.extract_contents(body)
