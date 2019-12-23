#!/usr/bin/env python3
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
        title = 'Volume %d' % vol['id']
        if not ('title' in vol and vol['title']):
            vol['title'] = title
        # end if
        # if not('title_lock' in vol and vol['title_lock']):
        #     if not ('title' in vol and vol['title']):
        #         vol['title'] = title
        #     # end if
        #     if not re.search(r'(book|vol|volume) .?\d+', vol['title'], re.I):
        #         vol['title'] = title + ' - ' + vol['title'].title()
        #     # end if
        #     vol['title'] = crawler.cleanup_text(vol['title'])
        # # end if
    # end for
# end def


def format_chapters(crawler: Crawler):
    for item in crawler.chapters:
        title = '#%d' % item['id']
        if not ('title' in item and item['title']):
            item['title'] = title
        # end if
        # if not('title_lock' in item and item['title_lock']):
        #     if not ('title' in item and item['title']):
        #         item['title'] = title
        #     # end if
        #     if not re.search(r'((ch(apter)?) )?.?\d+', item['title'], re.I):
        #         item['title'] = title + ' - ' + item['title'].title()
        #     # end if
        #     item['title'] = crawler.cleanup_text(item['title'])
        # # end if

        if not item['volume']:
            item['volume'] = (1 + (item['id'] - 1) // 100)
        # end if
        item['volume_title'] = 'Volume %d' % item['volume']
        for vol in crawler.volumes:
            if vol['id'] == item['volume']:
                item['volume_title'] = vol['title']
                vol['chapter_count'] += 1
                break
            # end if
        # end for
    # end for
# end def


def save_metadata(crawler, output_path):
    file_name = os.path.join(output_path, 'meta.json')
    data = {
        'url': crawler.novel_url,
        'title': crawler.novel_title,
        'author': crawler.novel_author,
        'cover': crawler.novel_cover,
        'volumes': crawler.volumes,
        'chapters': crawler.chapters,
    }
    with open(file_name, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    # end with
# end def
