# -*- coding: utf-8 -*-
"""
To get the novel info
"""
import re
import os
import json
from ..utils.crawler import Crawler


def format_novel(crawler: Crawler):
    crawler.novel_title = crawler.novel_title.strip()
    crawler.novel_author = crawler.novel_author.strip()
    # crawler.novel_title = crawler.cleanup_text(crawler.novel_title)
    # crawler.novel_author = crawler.cleanup_text(crawler.novel_author)
    format_volumes(crawler)
    format_chapters(crawler)
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
    # end for
# end def


def format_chapters(crawler: Crawler):
    for item in crawler.chapters:
        title = '#%d' % item['id']
        if not ('title' in item and item['title']):
            item['title'] = title
        # end if

        volume = [x for x in crawler.volumes if x['id'] == item['volume']]
        if len(volume) == 0:
            raise Exception('Unknown volume %s for chapter %s' % (item['volume'], item['id']))
        else:
            volume = volume[0]
        # end if

        item['volume_title'] = volume['title']

        volume['chapter_count'] += 1
        volume['final_chapter'] = item['id'] if volume['final_chapter'] < item['id'] else volume['final_chapter']
        volume['start_chapter'] = item['id'] if volume['start_chapter'] > item['id'] else volume['start_chapter']
    # end for
# end def


def save_metadata(crawler, output_path):
    data = {
        'url': crawler.novel_url,
        'title': crawler.novel_title,
        'author': crawler.novel_author,
        'cover': crawler.novel_cover,
        'volumes': crawler.volumes,
        'chapters': crawler.chapters,
        'rtl': crawler.is_rtl,
    }
    file_name = os.path.join(output_path, 'json', 'meta.json')
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    # end with
# end def
