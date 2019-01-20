#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil

NOT_IMPLEMENTED = Exception('Not Implemented')


class UserInterface:
    selections = ['all', 'last', 'first',
                  'page', 'range', 'volumes', 'chapters']
    output_formats = ['epub', 'mobi', 'html', 'text', 'docx', 'pdf']

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
        if len(search_results) == 0:
            return ''
        else:
            return search_results[0][1]
        # end if
    # end def

    def get_output_path(self, suggested_path):
        '''Returns a valid output path where the files are stored'''
        output_path = os.path.abspath(suggested_path)
        os.makedirs(output_path, exist_ok=True)
        return output_path
    # end def

    def get_output_formats(self):
        '''Returns a set of output formats'''
        return { x: True for x in self.output_formats }
    # end def

    def get_login_info(self):
        '''Returns the (email, password) pair for login'''
        return None
    # end if

    def get_range_selection(self, chapter_count, volume_count):
        '''Returns a choice of how to select the range of chapters to downloads'''
        raise NOT_IMPLEMENTED
    # end def

    def get_range_using_urls(self, crawler):
        '''Returns a range of chapters using start and end urls as input'''
        raise NOT_IMPLEMENTED
    # end def

    def get_range_using_index(self, chapter_count):
        '''Returns a range selected using chapter indices'''
        raise NOT_IMPLEMENTED
    # end def

    def get_range_from_volumes(self, volumes, times=0):
        '''Returns a range created using volume list'''
        raise NOT_IMPLEMENTED
    # end def

    def get_range_from_chapters(self, crawler, times=0):
        '''Returns a range created using individual chapters'''
        raise NOT_IMPLEMENTED
    # end def

    def should_pack_by_volume(self):
        '''Returns whether to generate single or multiple files by volumes'''
        return False  # False will generate a single file
    # end def

    def should_fetch_kindlegen(self):
        '''Whether to fetch kindlegen if it does not exists'''
        return True  # True will download kindlegen in the user directory to use it
    # end def
# end class
