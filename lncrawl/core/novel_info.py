import json
import math
import os
import re
from typing import Dict

from .. import constants as C
from .crawler import Crawler
from .exeptions import LNException


def __format_title(text):
    return re.sub(r"\s+", " ", str(text)).strip().title()


def __format_volume(crawler: Crawler, vol_id_map: Dict[int, int]):
    if not crawler.volumes:
        for i in range(math.ceil(len(crawler.chapters) / 100)):
            crawler.volumes.append({"id": i + 1})

    for index, vol in enumerate(crawler.volumes):
        if not isinstance(vol.get("id"), int) or vol["id"] < 0:
            raise LNException(f"Unknown volume id at index {index}")
        vol["title"] = __format_title(vol.get("title") or f"Volume {vol['id']}")
        vol["start_chapter"] = len(crawler.chapters)
        vol["final_chapter"] = 0
        vol["chapter_count"] = 0
        vol_id_map[vol["id"]] = index


def __format_chapters(crawler: Crawler, vol_id_map: Dict[int, int]):
    for index, item in enumerate(crawler.chapters):
        if not isinstance(item.get("id"), int) or item["id"] < 0:
            raise LNException(f"Unknown item id at index {index}")

        if isinstance(item.get("volume"), int):
            vol_index = vol_id_map.get(item["volume"], -1)
        else:
            vol_index = vol_id_map.get(index // 100 + 1, -1)
        assert vol_index >= 0 and vol_index < len(
            crawler.volumes
        ), f"Unknown volume for chapter {item['id']}"

        volume = crawler.volumes[vol_index]
        item["volume"] = volume["id"]
        item["volume_title"] = volume["title"]

        volume["start_chapter"] = min(volume["start_chapter"], item["id"])
        volume["final_chapter"] = max(volume["final_chapter"], item["id"])
        volume["chapter_count"] += 1

        item["title"] = __format_title(item.get("title") or "#%d" % item["id"])


def format_novel(crawler: Crawler):
    crawler.novel_title = __format_title(crawler.novel_title)
    crawler.novel_author = __format_title(crawler.novel_author)
    vol_id_map: Dict[int, int] = {}
    __format_volume(crawler, vol_id_map)
    __format_chapters(crawler, vol_id_map)
    crawler.volumes = [x for x in crawler.volumes if x["chapter_count"] > 0]


def save_metadata(app, completed=False):
    from ..core.app import App
    from .crawler import Crawler

    if not (isinstance(app, App) and isinstance(app.crawler, Crawler)):
        return

    data = {
        "url": app.crawler.novel_url,
        "title": app.crawler.novel_title,
        "author": app.crawler.novel_author,
        "cover": app.crawler.novel_cover,
        "volumes": app.crawler.volumes,
        "chapters": [
            {k: v for k, v in chap.items() if k != "body"}
            for chap in app.crawler.chapters
        ],
        "rtl": app.crawler.is_rtl,
        "session": {
            "completed": completed,
            "user_input": app.user_input,
            "login_data": app.login_data,
            "output_path": app.output_path,
            "output_formats": app.output_formats,
            "pack_by_volume": app.pack_by_volume,
            "good_file_name": app.good_file_name,
            "no_append_after_filename": app.no_append_after_filename,
            "download_chapters": [chap["id"] for chap in app.chapters],
        },
    }
    os.makedirs(app.output_path, exist_ok=True)
    file_name = os.path.join(app.output_path, C.META_FILE_NAME)
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
