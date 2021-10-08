# -*- coding: utf-8 -*-
"""
Use this template to create new sources.

TODO: Read the TODOs carefully.
TODO: You should remove all TODOs tag.
TODO: You can safely delete all [OPTIONAL] methods if you do not need them
"""
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class MyCrawlerName(Crawler):
    # TODO: [REQUIRED] Provide the URLs supported by this crawler.
    base_url = [
        'http://sample.url/'
    ]
    
    # TODO: [OPTIONAL] Set True if this crawler is for manga/manhua/manhwa.
    has_manga = False

    # TODO: [OPTIONAL] Set True if this source contains machine translations.
    machine_translation = False

    def initialize(self):
        # TODO: [OPTIONAL] This gets called before executing all other methods.
        pass
    # end def

    def login(self, email, password):
        # TODO: [OPTIONAL] This gets called before searching, getting novel info,
        #       or getting chapter list url. Cookies are managed automatically by
        #       a python requests Session.
        #
        # Examle: lnmtl.py, mtlednovels.py
        pass
    # end def

    def logout(self):
        # TODO: [OPTIONAL] Implement this if you think it is necessary to logout.
        pass
    # end def

    def search_novel(self, query):
        # TODO: [OPTIONAL] Return a list of search results using the query.
        #       The return object should be a list of objects having these fields:
        #         `title` - novel name [required]
        #         `url`   - novel url [required]
        #         `info`  - extra description about the novel [optional]
        #                   You can put the chapter / volume count / author etc.
        #                   Please keep it short, to not look bad on the console.
        #
        #       You may throw an Exception or empty list in case of failure.
        pass
    # end def

    def read_novel_info(self):
        # TODO: [REQUIRED] Get some necessary information about the novel.
        #       The current novel url is available at `self.novel_url`.
        #       Check the base lncrawl.core.crawler.Crawler class for useful methods.
        #
        #       `self.novel_title`: a string [required]
        #       `self.novel_autor`: a comma separated string. [optional]
        #       `self.novel_cover`: the cover image url [optional]
        #       `self.chapters`: A list of chapters. Each chapter should contain these keys:
        #          `id`     : the chapter number [required]
        #          `volume` : the volume number [required]
        #          `url`    : the link to download the chapter [required]
        #          `title`  : the title name [optional]
        #       `self.volumes`: Unique list of volumes used inside the chatpers.
        #          `id`     : the index of the volume [required]
        #          `title`  : the volume title [optional]
        #
        #       You may throw an Exception in case of failure
        pass
    # end def

    def download_chapter_body(self, chapter):
        # TODO: [REQUIRED] Download content of a single chapter and return it in a
        #       clean html format. You can use `chapter['url']` to get the contents.
        #
        #       To keep it simple, check `self.extract_contents` in the parent `Crawler` class.
        #       It extracts chapter contents given a soup Tag, and returns a clean HTML.
        pass
    # end def

    def get_chapter_index_of(self, url):
        # TODO: [OPTIONAL] It is useful for selecting chapter range to download using
        #       chapter urls. Return the index of chapter by given url or -1.
        #
        #       A default behavior has been implemented in the `Crawler` class.
        #       Delete this method if you want to use the default one.
        pass
    # end def

# end class
