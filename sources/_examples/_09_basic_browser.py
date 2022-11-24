# -*- coding: utf-8 -*-
"""
# TODO: Read the TODOs carefully and remove all existing comments in this file.

This is a sample using the BasicBrowserTemplate as a template. This template
provides a basic wrapper around the base Crawler. In case a scraper based request
fails with `ScraperNotSupported`, it retries with the webdriver based scraping.

Put your source file inside the language folder. The `en` folder has too many
files, therefore it is grouped using the first letter of the domain name.
"""
import logging
from typing import List

from lncrawl.models.chapter import Chapter
from lncrawl.models.search_result import SearchResult
from lncrawl.templates.browser.basic import BasicBrowserTemplate

logger = logging.getLogger(__name__)


# TODO: You can safely delete all [OPTIONAL] methods if you do not need them.
class MyCrawlerName(BasicBrowserTemplate):
    # TODO: [REQUIRED] Provide the URLs supported by this crawler.
    base_url = ["http://sample.url/"]

    # TODO: [OPTIONAL] Set True if this crawler is for manga/manhua/manhwa.
    has_manga = False

    # TODO: [OPTIONAL] Set True if this source contains machine translations.
    has_mtl = False

    # TODO: [OPTIONAL] This is called before all other methods.
    def initialize(self) -> None:
        # You can customize `TextCleaner` and other necessary things.
        pass

    # TODO: [OPTIONAL] This is called once per session before searching and fetching novel info.
    def login(self, username_or_email: str, password_or_token: str) -> None:
        # Examples:
        # - https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/mtlnovel.py
        # - https://github.com/dipu-bd/lightnovel-crawler/blob/master/sources/multi/ranobes.py
        pass

    # TODO: [OPTIONAL] If it is necessary to logout after session is finished, you can implement this.
    def logout(self):
        pass

    # TODO: [OPTIONAL] Search for novels with `self.scraper` requests
    def search_novel_in_scraper(self, query: str) -> List[SearchResult]:
        # raise ScraperNotSupported()
        pass

    # TODO: [OPTIONAL] Search for novels with `self.browser`
    def search_novel_in_browser(self, query: str) -> List[SearchResult]:
        pass

    # TODO: [OPTIONAL] Read novel info with `self.scraper` requests
    def read_novel_info_in_scraper(self) -> None:
        # The current input url is available at `self.novel_url`.
        # You can use `self.get_soup`, `self.get_json` etc. utilities to fetch contents.
        #
        # You must set the following parameters:
        #       `self.novel_title`: the title of the novel
        #       `self.chapters`: the list of all chapters
        #
        # The following paramters are optional but good to have:
        #       `self.novel_author`: a comma separated list of names
        #       `self.novel_cover`: the novel cover image url
        #       `self.volumes`: the list of all volumes
        #
        # You may throw an Exception in case of failure.
        # `raise ScraperNotSupported()` to use the browser only.
        pass

    # TODO: [REQUIRED] Read novel info with `self.browser`
    def read_novel_info_in_browser(self) -> None:
        # This gets called only when the `read_novel_info_in_scraper` fails.
        # The current input url is available at `self.novel_url`.
        # You can use `self.visit`, `self.browser.wait` etc. utilities.
        # Get a BeautifulSoup Tag instance from browser: `self.browser.find(..).as_tag()`
        #
        # You must set the following parameters:
        #       `self.novel_title`: the title of the novel
        #       `self.chapters`: the list of all chapters
        #
        # The following paramters are optional but good to have:
        #       `self.novel_author`: a comma separated list of names
        #       `self.novel_cover`: the novel cover image url
        #       `self.volumes`: the list of all volumes
        #
        # You may throw an Exception in case of failure.
        pass

    # TODO: [OPTIONAL] Download the chapter contents using the self.scraper requests
    def download_chapter_body_in_scraper(self, chapter: Chapter) -> str:
        # Use the `chapter['url']` to get the chapter contents.
        # You can use `self.get_soup`, `self.get_json` etc. utilities to fetch contents.
        # To clean chapter HTML easily, use `self.cleaner.extract_contents`.
        #
        # `raise ScraperNotSupported()` to use the browser only.
        pass

    # TODO: [REQUIRED] Download the chapter contents using the `self.browser`
    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        # Use the `chapter['url']` to get the chapter contents.
        # You can use `self.visit` to visit the chapter in browser tab.
        # There can be only one thread using the browser at a time.
        # Get a BeautifulSoup Tag instance from browser: `self.browser.find(..).as_tag()`
        # To clean chapter HTML easily, use `self.cleaner.extract_contents`.
        pass

    # TODO: [OPTIONAL] Return the index in self.chapters which contains a chapter URL
    def index_of_chapter(self, url: str) -> int:
        # To get more help, check the default implemention in the `Crawler` class.
        pass
