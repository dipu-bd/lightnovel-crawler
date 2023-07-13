# -*- coding: utf-8 -*-
import json
import logging
import re

from urllib.parse import quote

from bs4.element import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume
from lncrawl.models import Chapter

logger = logging.getLogger(__name__)

search_url = "/api/search?keyword=%s&index=0&limit=20"
chapter_list_url = "/api/chapters?id=%d&index=1&limit=15000"


class LightNovelsLive(Crawler):
    base_url = [
        "http://lightnovels.me/",
        "https://lightnovels.me/",
        "http://lightnovels.live/",
        "https://lightnovels.live/"
    ]

    has_manga = False
    has_mtl = False

    def search_novel(self, query):
        url = self.absolute_url(search_url % quote(query))
        data = self.get_json(url)

        results = []
        for item in data["results"]:
            results.append(
                {
                    "title": item["novel_name"],
                    "url": self.absolute_url("/novel" + item["novel_slug"]),
                    "info": f"Status: {item['status']} | Latest: {item['chapter_name']}",
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        script = soup.select_one('script#__NEXT_DATA__')
        assert isinstance(script, Tag), "No available novel info."

        data = json.loads(script.text)

        novel_info = data['props']['pageProps']['novelInfo']
        novel_id = int(novel_info['novel_id'])

        self.novel_title = novel_info['novel_name']
        self.novel_cover = self.absolute_url(novel_info['novel_image'])
        self.novel_author = ', '.join(
            [author['name'] for author in data['props']['pageProps']['authors']]
        )

        # Adds proper spacing in the synopsis. (lossy)
        #
        # Regex101 link: https://regex101.com/r/lajsXs/3
        for paragraph in re.split(r'[.!?](?=\w+)(?!\S+[.!?()]+(\s|\w))', novel_info['novel_description']):
            if paragraph is None:
                self.novel_synopsis += "<br/><br/>"
                continue

            self.novel_synopsis += paragraph

            if paragraph.endswith('!') | paragraph.endswith('?') | paragraph.endswith('.'):
                pass
            else:
                self.novel_synopsis += "."

        self.novel_tags = ', '.join(
            [genre['name'] for genre in data['props']['pageProps']['genres']]
        )

        url = self.absolute_url(chapter_list_url % novel_id)
        data = self.get_json(url)

        for index, item in enumerate(data['results']):
            chap_id = index + 1
            vol_id = index // 100 + 1
            if index % 100 == 0:
                self.volumes.append(
                    Volume(id=vol_id)
                )
            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    title=item['chapter_name'],
                    url=self.absolute_url(item["slug"])
                )
            )

    def download_chapter_body(self, chapter):
        tag = self.get_soup(chapter['url']).select_one(".chapter-content div")

        str_chapter = self.cleaner.extract_contents(tag).replace(r"\'", "'").strip()
        if str_chapter == "":
            print(f"  Warning: no contents in chapter {chapter['id']}, {chapter['title']}.")
            str_chapter = '<h4>Empty chapter.</h4>' +\
                          '<p><mark style="color:Green">Hint</mark>: ' +\
                          'reporting this to your provider <i>might</i> solve the issue.</p>'

        return str_chapter
