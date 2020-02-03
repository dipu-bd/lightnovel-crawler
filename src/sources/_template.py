# -*- coding: utf-8 -*-
"""
Use this template to create new sources.
TODO: Read the TODOs carefully.
TODO: You should remove all TODOs tag.
TODO: You can safely delete all [OPTIONAL] methods if you do not need them
"""
import logging
import re

from ..utils.crawler import Crawler

# TODO: Set a name for meaningful logging
logger = logging.getLogger(__name__)


class SampleCrawler(Crawler):
    # TODO: [REQUIRED] You must provide the source url first.
    base_url = ['http://sample.url/']

    def initialize(self):
        # TODO: [OPTIONAL] Initiaze your crawler, variables etc. It gets called at the
        #       beginning of the app.
        pass
    # end def

    def login(self, email, password):
        # TODO: [OPTIONAL] Login to the source using email and password.
        #       You can use `self.get_response` and `self.submit_form`
        #       methods from the parent class. They maintain cookies
        #       automatically for you.
        #
        # Examle sources: lnmtl, mtlednovels
        pass
    # end def

    def logout(self):
        # TODO: [OPTIONAL] Logout from the site. Not that necessary,
        #       but still it is nice to logout after you are done.
        #
        # Examle sources: lnmtl, mtlednovels
        pass
    # end def

    def search_novel(self, query):
        # TODO: [OPTIONAL] Gets a list of results matching the given query.
        #       `self.novel_url` contains the query. Search for novels using it,
        #       and return a list of dictionary with the following keys:
        #         `title` - novel name [required]
        #         `url`   - novel url [required]
        #         `info`  - short description about the novel [optional]
        #                   You can put the chapter & volume count or
        #                   latest chapter names, etc. here.
        #                   Please keep it short, to not look bad on the console.
        #
        #       You may throw an Exception or empty list in case of failure.
        pass
    # end def

    def read_novel_info(self):
        # TODO: [MUST IMPLEMENT] It is used to get the novel title and chapter list.
        #       Use the `self.novel_url` to get the following info:
        #
        #       `self.novel_title`: Must be set
        #       `self.novel_autor`: Comma separated list of author [optional]
        #       `self.novel_cover`: Cover image url [optional]
        #       `self.volumes`: A list of volumes. Each volume should contain these keys:
        #          `id`     : the index of the volume
        #          `title`  : the volume title [optional]
        #       `self.chapters`: A list of chapters. Each chapter should contain these keys:
        #          `id`     : the chapter number [required]
        #          `title`  : the title name [optional]
        #          `volume` : the volume number [required]
        #          `url`    : the link where to download the chapter [required]
        #
        #       You may throw an Exception in case of failure
        pass
    # end def

    def get_chapter_index_of(self, url):
        # TODO: [OPTIONAL] Return the index of chapter by given url or -1
        #       A default behavior has been implemented in the parent class.
        #       Delete this method if you want to use the default one.
        #       By default, it should return the first index of chapter from the
        #       `self.chapters` that has `url` property matching the given url.
        pass
    # end def

    def download_chapter_body(self, chapter):
        # TODO: [MUST IMPLEMENT] Download body of a single chapter and return a
        #       clean html format. You may use `chapter['url']` here.
        #
        # NOTE: Set `chapter['body_lock'] = True` to disable post-formatting.
        #       It can be useful in non-english sources, e.g. aixdzs, qidiancom, tiknovel
        #
        #       Return an empty body if anything goes wrong. But you should not return `None`.
        pass
    # end def
# end class
