from __future__ import annotations
from functools import lru_cache
from typing import List
from pathlib import Path
import json
from ... import constants
from .Novel import Novel, NovelFromSource

from . import read_novel_info

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .downloader.Job import JobHandler, FinishedJob

jobs: dict[str, FinishedJob | JobHandler] = {}


LIGHTNOVEL_FOLDER = Path(constants.DEFAULT_OUTPUT_PATH)
if not LIGHTNOVEL_FOLDER.exists():
    LIGHTNOVEL_FOLDER.mkdir()


@lru_cache
def findSourceWithPath(novel_and_source_path: Path) -> NovelFromSource | None:
    """
    Find the NovelFromSource object corresponding to the path
    """
    novel = None
    for n in all_downloaded_novels:
        if novel_and_source_path.parent == n.path:
            novel = n
            break
    if not novel:
        return None

    source = None
    for s in novel.sources:
        if novel_and_source_path == s.path:
            source = s
            break
    if not source:
        return None

    return source


all_downloaded_novels: List[Novel] = []
for novel_folder in LIGHTNOVEL_FOLDER.iterdir():
    if novel_folder.is_dir():
        all_downloaded_novels.append(read_novel_info.get_novel_info(novel_folder))


import threading, time
def update_novels_stats():
    """Periodic function to update each novels stats"""
    while True:
        time.sleep(600) # 10 minutes
        for novel in all_downloaded_novels:
            if not novel.path:
                continue
            with open(novel.path / "stats.json", "w", encoding="utf-8") as f:
                novel_stats = {
                    "clicks": novel.clicks,
                    "ratings": novel.ratings,
                }

                json.dump(novel_stats, f, indent=4)

        print("Updated novels stats")


threading.Thread(target=update_novels_stats, daemon=True).start()
