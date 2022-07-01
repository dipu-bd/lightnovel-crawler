from __future__ import annotations
from functools import lru_cache
from typing import List
from pathlib import Path
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

