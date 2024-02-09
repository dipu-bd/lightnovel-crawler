# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_search_url = "/search/autocomplete?query=%s"
chapter_load_url = "/novel/load-chapters"


class LightnovelReader(Crawler):
    base_url = [
        "https://lightnovelreader.me/",
        "https://www.lightnovelreader.me/",
        "https://lnreader.org/",
        "https://www.lnreader.org/",
        "http://readlightnovel.online/",
        "https://readlitenovel.com/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(
            [
                "center",
            ]
        )
        self.cleaner.bad_css.update(
            [
                'div[style="display:none"]',
                'div[class*="hidden"]',
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                r"Please read this chapter at www.lightnovelreader.com for faster releases",
            ]
        )

    def search_novel(self, query):
        self.get_response(self.home_url)

        url = self.absolute_url(novel_search_url % quote(query))
        data = self.get_json(url)

        results = []
        for item in data["results"]:
            results.append(
                {
                    "title": str(item["original_title"]),
                    "url": self.absolute_url(item["link"]),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)

        response = self.get_response(self.novel_url)
        html_text = response.content.decode("utf8", "ignore")
        html_text = html_text.replace(r"</body>", "").replace(r"</html>", "")
        html_text += "</body></html>"
        soup = self.make_soup(html_text)

        possible_title = soup.select_one(".section-header-title")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".novels-detail-left img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possibles_syn = soup.select(".row .col-md-12.mb-3")
        for i, e in enumerate(possibles_syn):
            if e.text.strip() == "DESCRIPTION":
                break
        if (len(possibles_syn) >= i + 1) and isinstance(possibles_syn[i + 1], Tag):
            self.novel_synopsis = self.cleaner.extract_contents(possibles_syn[i + 1])
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        tags = soup.select(".novels-detail-right-in-right a[href*=category]")
        self.novel_tags = [tag.text.strip() for tag in tags if isinstance(tag, Tag)]
        logger.info("Novel genre: %s", self.novel_tags)

        self.novel_author = ', '.join([
            a.text.strip()
            for a in soup.select('.container .novels-detail-right-in-right a[href*="/author/"]')
        ])
        logger.info("Novel author: %s", self.novel_author)

        # possible_novel_id = soup.select_one('.js-load-chapters')
        # assert isinstance(possible_novel_id, Tag)
        # novel_id = str(possible_novel_id['data-novel-id']).strip()
        # logger.info('# novel id = %s', novel_id)

        # response = self.submit_form(
        #     self.absolute_url(chapter_load_url),
        #     data='novelId=%s' % novel_id,
        #     headers={
        #         'accept': '*/*',
        #         'x-requested-with': 'XMLHttpRequest',
        #         'origin': self.home_url.strip('/'),
        #         'referer': self.novel_url.strip('/'),
        #     },
        # )
        # soup = self.make_soup(response)

        # volumes = set()
        # for a in reversed(soup.select('a')):
        #     chap_id = len(self.chapters) + 1
        #     vol_id = len(self.chapters) // 100 + 1
        #     volumes.add(vol_id)
        #     self.chapters.append({
        #         'id': chap_id,
        #         'volume': vol_id,
        #         'title': a.text.strip(),
        #         'url': self.absolute_url(a['href']),
        #     })
        # # end for

        # self.volumes = [{'id': x} for x in volumes]

        for tab in reversed(
            soup.select(".novels-detail-chapters-btn-list a[data-tab]")
        ):
            vol_id = len(self.volumes) + 1
            self.volumes.append({"id": vol_id})
            for a in reversed(
                soup.select(".novels-detail-chapters#%s a" % tab["data-tab"])
            ):
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "title": a.text.strip(),
                        "url": self.absolute_url(a["href"]),
                    }
                )

    def download_chapter_body(self, chapter):
        response = self.get_response(chapter["url"])
        html_text = response.content.decode("utf8", "ignore")
        html_text = html_text.replace(r"</body>", "").replace(r"</html>", "")
        html_text += "</body></html>"
        soup = self.make_soup(html_text)
        body = soup.select_one("#chapterText")
        return self.cleaner.extract_contents(body)
