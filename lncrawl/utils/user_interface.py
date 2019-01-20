#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil

NOT_IMPLEMENTED = Exception('Not Implemented')


# TODO: All methods inside the user-interface is required and must be implemented.
class UserInterface:
    selections = ['all', 'last', 'first',
                  'page', 'range', 'volumes', 'chapters']

    def get_novel_url(self):
        '''Returns a novel page url or a query'''
        raise NOT_IMPLEMENTED
    # end def

    def get_crawlers_to_search(self, links):
        '''Returns user choice to search the choosen sites for a novel'''
        raise NOT_IMPLEMENTED
    # end def

    def choose_a_novel(self, search_results):
        '''Choose a single novel url from the search result'''
        # The search_results is an array of (novel_title, novel_url).
        # This method should return a single novel_url only
        if len(search_results) == 0:
            return ''
        elif len(search_results) == 1:
            return search_results[0][1]
        else:
            raise NOT_IMPLEMENTED
        # end if
    # end def

    def get_output_path(self, suggested_path):
        '''Returns a valid output path where the files are stored'''
        # TODO: You should return a valid absolute path.
        # The parameter suggested_path is a suggested directory. It is not
        # gurranteed to be valid.
        output_path = os.path.abspath(suggested_path)
        os.makedirs(output_path, exist_ok=True)
        return output_path
    # end def

    def get_login_info(self):
        '''Returns the (email, password) pair for login'''
        # Returning None if you want to skip login
        return None
    # end if

    def get_range_selection(self, chapter_count, volume_count):
        '''Returns a choice of how to select the range of chapters to downloads'''
        # TODO: Return a key from `self.selections`
        raise NOT_IMPLEMENTED
    # end def

    def get_range_using_urls(self, crawler):
        '''Returns a range of chapters using start and end urls as input'''
        # TODO: Return a list of chapters to download
        raise NOT_IMPLEMENTED
    # end def

    def get_range_using_index(chapter_count):
        '''Returns a range selected using chapter indices'''
        # TODO: Return a list of chapters to download
        raise NOT_IMPLEMENTED
    # end def

    def get_range_from_volumes(volumes, times=0):
        '''Returns a range created using volume list'''
        # TODO: Return a list of chapters to download
        raise NOT_IMPLEMENTED
    # end def

    def range_from_chapters(crawler, times=0):
        '''Returns a range created using individual chapters'''
        # TODO: Return a list of chapters to download
        raise NOT_IMPLEMENTED
    # end def

    def pack_by_volume():
        '''Returns whether to generate single or multiple files by volumes'''
        return False  # False will generate a single file
    # end def

    def should_fetch_kindlegen():
        '''Whether to fetch kindlegen if it does not exists'''
        return True  # True will download kindlegen in the user directory to use it
    # end def
# end class
