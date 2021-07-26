# -*- coding: utf-8 -*-
"""
To get the novel info
"""
import json
import os
import re

from .. import constants as C
from lncrawl.core.crawler import Crawler


def __format_title(text):
    return re.sub(r'\s+', ' ', text).strip()
# end def


def format_novel(crawler: Crawler):
    crawler.novel_title = __format_title(crawler.novel_title)
    crawler.novel_author = __format_title(crawler.novel_author)
    # crawler.novel_title = crawler.cleanup_text(crawler.novel_title)
    # crawler.novel_author = crawler.cleanup_text(crawler.novel_author)
    format_volumes(crawler)
    format_chapters(crawler)
    crawler.volumes = [x for x in crawler.volumes if x['chapter_count'] > 0]
# end def


def format_volumes(crawler: Crawler):
    for vol in crawler.volumes:
        vol['chapter_count'] = 0
        vol['final_chapter'] = 0
        vol['start_chapter'] = 1e8
        title = 'Volume %d' % vol['id']
        if not ('title' in vol and vol['title']):
            vol['title'] = title
        # end if
        vol['title'] = __format_title(vol['title'])
    # end for
# end def


def format_chapters(crawler: Crawler):
    for item in crawler.chapters:
        title = '#%d' % item['id']
        if not ('title' in item and item['title']):
            item['title'] = title
        # end if
        item['title'] = __format_title(item['title'])

        volume = [x for x in crawler.volumes if x['id'] == item['volume']]
        if len(volume) == 0:
            raise Exception('Unknown volume %s for chapter %s' %
                            (item['volume'], item['id']))
        else:
            volume = volume[0]
        # end if

        item['volume_title'] = volume['title']

        volume['chapter_count'] += 1
        volume['final_chapter'] = item['id'] if volume['final_chapter'] < item['id'] else volume['final_chapter']
        volume['start_chapter'] = item['id'] if volume['start_chapter'] > item['id'] else volume['start_chapter']
    # end for
# end def


def save_metadata(app, completed=False):
    from ..core.app import App
    from lncrawl.core.crawler import Crawler
    if not isinstance(app, App) and not isinstance(app.crawler, Crawler):
        return

    data = {
        'url': app.crawler.novel_url,
        'title': app.crawler.novel_title,
        'author': app.crawler.novel_author,
        'cover': app.crawler.novel_cover,
        'volumes': app.crawler.volumes,
        'chapters': [
            {k: v for k, v in chap.items() if k != 'body'}
            for chap in app.crawler.chapters
        ],
        'rtl': app.crawler.is_rtl,
        'session': {
            'completed': completed,
            'user_input': app.user_input,
            'login_data': app.login_data,
            'output_path': app.output_path,
            'output_formats': app.output_formats,
            'pack_by_volume': app.pack_by_volume,
            'good_file_name':  app.good_file_name,
            'no_append_after_filename': app.no_append_after_filename,
            'download_chapters': [chap['id'] for chap in app.chapters]
        }
    }
    os.makedirs(app.output_path, exist_ok=True)
    file_name = os.path.join(app.output_path, C.META_FILE_NAME)
    with open(file_name, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    # end with
# end def
