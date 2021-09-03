# -*- coding: utf-8 -*-
import logging
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from lncrawl.core.crawler import Crawler
from slugify import slugify

from .. import constants as C
from ..binders import available_formats, generate_books
from ..core.sources import crawler_list, rejected_sources
from .downloader import download_chapter_images, download_chapters
from .novel_info import format_novel, save_metadata
from .novel_search import search_novels

logger = logging.getLogger(__name__)


class App:
    '''Bots are based on top of an instance of this app'''

    def __init__(self):
        self.progress = 0
        self.user_input = None
        self.crawler_links: List[str] = []
        self.crawler: Optional[Crawler] = None
        self.login_data: Optional[Tuple[str, str]] = None
        self.search_results = []
        self.output_path = C.DEFAULT_OUTPUT_PATH
        self.pack_by_volume = False
        self.chapters: List[Dict[str, Any]] = []
        self.book_cover = None
        self.output_formats: Dict[str, bool] = {}
        self.archived_outputs = None
        self.good_file_name: str = ''
        self.no_append_after_filename = False
    # end def

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
                str(link)
                for link, crawler in crawler_list.items()
                if 'search_novel' in crawler.__dict__
            ]
        # end if
    # end def

    def search_novel(self):
        '''Requires: user_input, crawler_links'''
        '''Produces: search_results'''
        logger.info('Searching for novels in %d sites...',
                    len(self.crawler_links))

        search_novels(self)

        if not self.search_results:
            raise Exception('No results for: %s' % self.user_input)
        # end if

        logger.info('Total %d novels found from %d sites',
                    len(self.search_results), len(self.crawler_links))
    # end def

    # ----------------------------------------------------------------------- #

    def init_crawler(self, novel_url):
        if not novel_url:
            return
        # end if

        parsed_url = urlparse(novel_url)
        base_url = '%s://%s/' % (parsed_url.scheme, parsed_url.hostname)
        if base_url in rejected_sources:
            raise Exception('Source is rejected. Reason: ' + rejected_sources[base_url])
        # end if

        CrawlerType = crawler_list.get(base_url)
        if not CrawlerType:
            raise Exception('No crawler found for ' + base_url)
        # end if

        logger.info('Initializing crawler for: %s [%s]',
                    base_url, getattr(CrawlerType, 'file_path', '.'))
        self.crawler = CrawlerType()
        self.crawler.home_url = base_url
        self.crawler.novel_url = novel_url
    # end def

    def can_do(self, prop_name):
        return prop_name in self.crawler.__class__.__dict__
    # end def

    def get_novel_info(self):
        '''Requires: crawler, login_data'''
        '''Produces: output_path'''
        if not isinstance(self.crawler, Crawler):
            raise Exception('No crawler is selected')

        self.crawler.initialize()
        self.crawler.scraper.headers['origin'] = self.crawler.home_url
        self.crawler.scraper.headers['referer'] = self.crawler.home_url

        if self.can_do('login') and self.login_data:
            logger.debug('Login with %s', self.login_data)
            self.crawler.login(*list(self.login_data))
        # end if

        print('Retrieving novel info...')
        print(self.crawler.novel_url)
        self.crawler.read_novel_info()
        print('NOVEL: %s' % self.crawler.novel_title)
        print('%d volumes and %d chapters found' %
              (len(self.crawler.volumes), len(self.crawler.chapters)))

        format_novel(self.crawler)

        if not self.good_file_name:
            self.good_file_name = slugify(
                self.crawler.novel_title,
                max_length=50,
                separator=' ',
                lowercase=False,
                word_boundary=True,
            )
        # end if

        source_name = slugify(urlparse(self.crawler.home_url).netloc)
        self.output_path = os.path.join(C.DEFAULT_OUTPUT_PATH, source_name, self.good_file_name)
    # end def

    # ----------------------------------------------------------------------- #
    def start_download(self):
        '''Requires: crawler, chapters, output_path'''
        if not self.output_path or not os.path.isdir(self.output_path):
            raise Exception('Output path is not defined')
        # end if

        assert self.crawler

        save_metadata(self)
        download_chapters(self)
        save_metadata(self)
        download_chapter_images(self)
        save_metadata(self, True)

        if not self.output_formats.get('json', False):
            shutil.rmtree(os.path.join(self.output_path, 'json'), ignore_errors=True)
        # end if

        if self.can_do('logout'):
            self.crawler.logout()
        # end if
    # end def

    # ----------------------------------------------------------------------- #

    def bind_books(self):
        '''Requires: crawler, chapters, output_path, pack_by_volume, book_cover, output_formats'''
        logger.info('Processing data for binding')
        assert self.crawler

        data = {}
        if self.pack_by_volume:
            for vol in self.crawler.volumes:
                # filename_suffix = 'Volume %d' % vol['id']
                filename_suffix = 'Chapter %d-%d' % (
                    vol['start_chapter'], vol['final_chapter'])
                data[filename_suffix] = [
                    x for x in self.chapters
                    if x['volume'] == vol['id']
                    and len(x['body']) > 0
                ]
            # end for
        else:
            first_id = self.chapters[0]['id']
            last_id = self.chapters[-1]['id']
            vol = 'c%s-%s' % (first_id, last_id)
            data[vol] = self.chapters
        # end if

        generate_books(self, data)
    # end def

    # ----------------------------------------------------------------------- #

    def compress_books(self, archive_singles=False):
        logger.info('Compressing output...')

        # Get which paths to be archived with their base names
        path_to_process = []
        for fmt in available_formats:
            root_dir = os.path.join(self.output_path, fmt)
            if os.path.isdir(root_dir):
                path_to_process.append([
                    root_dir,
                    self.good_file_name + ' (' + fmt + ')'
                ])
            # end if
        # end for

        # Archive files
        self.archived_outputs = []
        for root_dir, output_name in path_to_process:
            file_list = os.listdir(root_dir)
            if len(file_list) == 0:
                logger.info('It has no files: %s', root_dir)
                continue
            # end if

            archived_file = None
            if len(file_list) == 1 and not archive_singles \
                    and not os.path.isdir(os.path.join(root_dir, file_list[0])):
                logger.info('Not archiving single file inside %s' % root_dir)
                archived_file = os.path.join(root_dir, file_list[0])
            else:
                base_path = os.path.join(self.output_path, output_name)
                logger.info('Compressing %s to %s' % (root_dir, base_path))
                archived_file = shutil.make_archive(
                    base_path,
                    format='zip',
                    root_dir=root_dir,
                )
                print('Compressed:', os.path.basename(archived_file))
            # end if

            if archived_file:
                self.archived_outputs.append(archived_file)
            # end if
        # end for
    # end def
# end class
