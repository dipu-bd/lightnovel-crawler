#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import shutil
import logging
from slugify import slugify

from ..spiders import crawler_list
from ..binders import bind_books, available_formats
from .downloader import download_chapters
from .novel_info import format_volumes, format_chapters, save_metadata


logger = logging.getLogger('APP')


class App:
    progress = 0
    user_input = None
    crawler_links = None
    crawler = None
    login_data = ()
    search_results = []
    output_path = None
    pack_by_volume = False
    chapters = []
    book_cover = None
    output_formats = None
    archived_outputs = None
    good_file_name = None

    # ----------------------------------------------------------------------- #

    def initialize(self):
        logger.info('Initialized App')
    # end def

    def destroy(self):
        if self.crawler:
            self.crawler.destroy()
        # end if
        self.chapters.clear()
        logger.info('Destroyed App')
    # end def

    # ----------------------------------------------------------------------- #

    def init_search(self):
        '''Requires: user_input'''
        '''Produces: [crawler, output_path] or [crawler_links]'''
        if not self.user_input:
            raise Exception('User input is not valid')
        # end if

        if self.user_input.startswith('http'):
            logger.info('Detected URL input')
            self.init_crawler(self.user_input)
        else:
            logger.info('Detected query input')
            self.crawler_links = [
                link for link in sorted(crawler_list.keys())
                if 'search_novel' in crawler_list[link].__dict__
            ]
        # end if
    # end def

    def search_novel(self):
        '''Requires: user_input, crawler_links'''
        '''Produces: search_results'''
        logger.warn('Searching for novels in %d sites...',
                    len(self.crawler_links))
        _checked = {}
        self.search_results = []
        for link in self.crawler_links:
            logger.info('Searching: %s with "%s"', link, self.user_input)
            try:
                crawler = crawler_list[link]
                if crawler in _checked:
                    continue
                # end if
                _checked[crawler] = True

                instance = crawler()
                instance.home_url = link.strip('/')
                results = instance.search_novel(self.user_input)
                self.search_results += results
                logger.debug(results)
                logger.info('%d results from %s', len(results), link)
            except Exception as ex:
                logger.debug(ex)
            # end try
        # end for
        if len(self.search_results) == 0:
            raise Exception('No results for: %s' % self.user_input)
        # end if
        logger.info('Total %d novels found from %d sites',
                    len(self.search_results), len(self.crawler_links))
    # end def

    # ----------------------------------------------------------------------- #

    def init_crawler(self, novel_url):
        '''Requires: [user_input]'''
        '''Produces: crawler'''
        if not novel_url:
            return
        for home_url, crawler in crawler_list.items():
            if novel_url.startswith(home_url):
                logger.info('Initializing crawler for: %s', home_url)
                self.crawler = crawler()
                self.crawler.novel_url = novel_url
                self.crawler.home_url = home_url.strip('/')
                break
            # end if
        # end for
        if not self.crawler:
            raise Exception('No crawlers were found')
        # end if
    # end def

    def can_do(self, prop_name):
        return prop_name in self.crawler.__class__.__dict__
    # end def

    def get_novel_info(self):
        '''Requires: crawler, login_data'''
        '''Produces: output_path'''
        self.crawler.initialize()

        if self.can_do('login') and self.login_data:
            logger.debug(self.login_data)
            self.crawler.login(*self.login_data)
        # end if

        logger.warn('Retrieving novel info...')
        self.crawler.read_novel_info()
        logger.warn('NOVEL: %s', self.crawler.novel_title)

        format_volumes(self.crawler)
        format_chapters(self.crawler)

        self.good_file_name = slugify(
            self.crawler.novel_title,
            max_length=50,
            separator=' ',
            lowercase=False,
            word_boundary=True,
        )
        self.output_path = os.path.join('Lightnovels', self.good_file_name)
    # end def

    # ------------------------------------------------------------------------#
    def start_download(self):
        '''Requires: crawler, chapters, output_path'''
        if not os.path.exists(self.output_path):
            raise Exception('Output path is not defined')
        # end if

        save_metadata(self.crawler, self.output_path)
        download_chapters(self)

        if self.can_do('logout'):
            self.crawler.logout()
        # end if
    # end def

    # ------------------------------------------------------------------------#

    def bind_books(self):
        '''Requires: crawler, chapters, output_path, pack_by_volume, book_cover, output_formats'''
        logger.info('Processing data for binding')
        data = {}
        if self.pack_by_volume:
            for vol in self.crawler.volumes:
                data['Volume %d' % vol['id']] = [
                    x for x in self.chapters
                    if x['volume'] == vol['id']
                    and len(x['body']) > 0
                ]
            # end for
        else:
            data[''] = self.chapters
        # end if

        bind_books(self, data)
    # end def

    # ------------------------------------------------------------------------#

    def compress_output(self, archive_singles=False):
        logger.info('Compressing output...')

        # Check if whole output folder is to be archived
        is_all = True
        if self.output_formats:
            for key in available_formats:
                if not self.output_formats[key]:
                    is_all = False
                    break
                # end if
            # end for
        # end if
        logger.info('Compressing whole directory: %s' % bool(is_all))

        # Get which paths to be archived with their base names
        path_to_process = []
        if is_all:
            path_to_process.append((self.output_path, self.good_file_name))
        else:
            for fmt, val in self.output_formats.items():
                if val:
                    path_to_process.append((
                        os.path.join(self.output_path, fmt),
                        '%s (%s)' % (self.good_file_name, fmt),
                    ))
                # end if
            # end for
        # end if
        logger.info('Processing %d directories' % len(path_to_process))

        # Archive files
        self.archived_outputs = []
        for path, base_name in path_to_process:
            archived = None
            file_list = os.listdir(path)
            if len(file_list) == 0:
                logger.info('It has no files: %s', path)
                continue # No files to archive
            elif len(file_list) == 1 and not archive_singles:
                logger.info('Not archiving single file inside %s' % path)
                archived = os.path.join(path, file_list[0])
            else:
                logger.info('Compressing %s to %s' % (path, base_name))
                base_path = os.path.join(self.output_path, '..', base_name)
                archived = shutil.make_archive(
                    os.path.normpath(base_path),
                    'zip',
                    root_dir=path,
                )
            # end if
            self.archived_outputs.append(archived)
        # end for

        logger.warn('Compressed: %s' % '\n\t'.join(self.archived_outputs))
    # end def
# end class
