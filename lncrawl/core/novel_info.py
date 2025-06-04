import math
import re
from typing import Dict

from ..models import Chapter, Volume
from .crawler import Crawler
from .exeptions import LNException


def __format_title(text):
    return re.sub(r"\s+", " ", str(text)).strip().title()


def __format_volume(crawler: Crawler, vol_id_map: Dict[int, int]):
    if crawler.volumes:
        crawler.volumes = [
            vol if isinstance(vol, Volume) else Volume(**vol)
            for vol in sorted(crawler.volumes, key=lambda x: x.get("id"))
        ]
    else:
        for i in range(math.ceil(len(crawler.chapters) / 100)):
            crawler.volumes.append(Volume(id=i + 1))

    for index, vol in enumerate(crawler.volumes):
        if not isinstance(vol.id, int) or vol.id < 0:
            raise LNException(f"Invalid volume id at index {index}")
        vol.title = __format_title(vol.title or f"Volume {vol.id}")
        vol.start_chapter = len(crawler.chapters)
        vol.final_chapter = 0
        vol.chapter_count = 0
        vol_id_map[vol.id] = index


def __format_chapters(crawler: Crawler, vol_id_map: Dict[int, int]):
    crawler.chapters = [
        chap if isinstance(chap, Chapter) else Chapter(**chap)
        for chap in sorted(crawler.chapters, key=lambda x: x.get("id"))
    ]
    for index, item in enumerate(crawler.chapters):
        if not isinstance(item, Chapter):
            item = crawler.chapters[index] = Chapter(**item)

        if not isinstance(item.id, int) or item.id < 0:
            raise LNException(f"Unknown item id at index {index}")

        if item.volume:
            vol_index = vol_id_map.get(item.volume, -1)
        else:
            vol_index = vol_id_map.get(index // 100 + 1, -1)
        assert vol_index >= 0 and vol_index < len(crawler.volumes), \
            f"Unknown volume for chapter {item['id']}"

        volume = crawler.volumes[vol_index]
        item.volume = volume.id
        item.volume_title = volume.title
        item.title = __format_title(item.title or f"#{item.id}")

        volume.chapter_count = (volume.chapter_count or 0) + 1
        if not volume.start_chapter or item.id < volume.start_chapter:
            volume.start_chapter = item.id
        if not volume.final_chapter or item.id > volume.final_chapter:
            volume.final_chapter = item.id


def format_novel(crawler: Crawler):
    crawler.novel_title = __format_title(crawler.novel_title)
    crawler.novel_author = __format_title(crawler.novel_author)
    vol_id_map: Dict[int, int] = {}
    __format_volume(crawler, vol_id_map)
    __format_chapters(crawler, vol_id_map)
    crawler.volumes = [x for x in crawler.volumes if x["chapter_count"] > 0]
