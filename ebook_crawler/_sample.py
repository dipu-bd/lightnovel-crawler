#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use this sample to create new sources
"""
import json
import logging
import re
from .utils.crawler import Crawler

logger = logging.getLogger('CHANGE_THIS_NAME')


class SampleCrawler(Crawler):
    @property
    def supports_login(self):
        '''Whether the crawler supports login() and logout method'''
        # TODO: Pass False or delete this method if this crawler
        #       does not support login.
        return False
    # end def

    def login(self, email, password):
        # TODO: You can just delete this method if not necessary.
        #       You can use `self.get_response` and `self.submit_form`
        #       methods from the parent class. They maintain cookies
        #       automatically for you.
        pass
    # end def

    def logout(self):
        # TODO: You can just delete this method if not necessary.
        #       This can also be used for disposing resources, as it gets
        #       called at the end of downloading all chapter bodies.
        pass
    # end def

    def read_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        # TODO: This method must be implemented to get the `novel_title`.
        #       You may or may not set the novel_cover, novel_author, volumes
        #       and chapter list, but the `novel_title` must be set here.
        pass
    # end def

    def download_chapter_list(self):
        '''Download list of chapters and volumes.'''
        # TODO: If you already got chapter list inside read_novel_info,
        #       implementing this one is not necessary. Just delete it.
        pass
    # end def

    def get_chapter_index_of(self, url):
        '''Return the index of chapter by given url or -1'''
        # TODO: A default behavior has been implemented in the parent class.
        #       Delete this method if you want to use the default one.
        pass
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        # TODO: This method must be implemented. Return an empty body if
        #       something goes wrong. You should not return None.
        pass
    # end def
# end class
