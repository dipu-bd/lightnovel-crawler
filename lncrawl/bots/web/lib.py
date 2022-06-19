from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional
import json
from urllib.parse import quote_plus
from pathlib import Path
from ... import constants


class FinishedJob:
    is_finished = True
    is_busy = False
    last_action = "Finished"

    def __init__(self, success, message, end_date):
        print(f"FinishedJob: {success}, {message}, {end_date}")
        self.success = success
        self.message = message
        self.end_date = end_date

    def is_busy(self):
        return False

    def get_status(self):
        return self.message

    def destroy(self):
        pass


jobs = {}


LIGHTNOVEL_FOLDER = Path(constants.DEFAULT_OUTPUT_PATH)


@dataclass(init=False)
class Novel:
    title: str
    path: Path
    cover: Path
    author: str
    chapter_count: int
    source_count: int
    latest: str
    volumes: int
    sources: list
    slug: str
    source_slug: Optional[str] = None
    first: Optional[str] = None
    summary: Optional[str] = None


def get_novel_info(novel_folder: Path):

    novel = Novel()
    novel.path = novel_folder.absolute()
    novel.slug = quote_plus(novel_folder.name)

    novel.title = None
    novel.cover = None
    novel.author = None
    novel.chapter_count = None
    novel.latest = None
    novel.volumes = None
    novel.sources = []

    for source_folder in novel_folder.iterdir():
        if not novel.cover and (source_folder / "cover.jpg").exists():
            novel.cover = f"{novel_folder.name}/{source_folder.name}/cover.jpg"

        if (source_folder / "meta.json").exists():
            with open(source_folder / "meta.json", "r", encoding="utf-8") as f:
                meta = json.load(f)
            novel.source_slug = quote_plus(source_folder.name)

        if not novel.author and "author" in meta:
            novel.author = meta["author"]

        if not novel.chapter_count:
            novel.chapter_count = len(meta["chapters"])

        if not novel.latest:
            novel.latest = meta["chapters"][-1]["title"]

        if not novel.volumes:
            novel.volumes = len(meta["volumes"])
        
        if not novel.title:
            novel.title = meta["title"]

        novel.sources.append(source_folder.name)

    if not novel.title:
        novel.title = novel_folder.name
    novel.source_count = len(novel.sources)
    return novel


@lru_cache
def get_novel_info_source(source_folder: Path):
    novel = Novel()
    novel.path = source_folder.parent.absolute()
    novel.slug = quote_plus(source_folder.parent.name)
    novel.source_slug = quote_plus(source_folder.name)
    novel.sources = [e.name for e in source_folder.parent.iterdir()]
    novel.source_count = len(novel.sources)

    novel.cover = (
        f"{source_folder.parent.name}/{source_folder.name}/cover.jpg"
        if (source_folder / "cover.jpg").exists()
        else None
    )
    if (source_folder / "meta.json").exists():
        with open(source_folder / "meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

        novel.author = meta["author"] if "author" in meta else None
        novel.chapter_count = len(meta["chapters"]) if "chapters" in meta else None
        novel.latest = (
            meta["chapters"][-1]["title"]
            if "chapters" in meta
            and len(meta["chapters"]) > 0
            and "title" in meta["chapters"][-1]
            else None
        )
        novel.volumes = len(meta["volumes"]) if "volumes" in meta else None
        novel.first = (
            meta["chapters"][0]["title"]
            if "chapters" in meta
            and len(meta["chapters"]) > 0
            and "title" in meta["chapters"][0]
            else None
        )
        novel.title = meta["title"] if "title" in meta else None
    
    if not novel.title:
        novel.title = source_folder.parent.name


    return novel


all_downloaded_novels: List[Novel] = []
for novel_folder in LIGHTNOVEL_FOLDER.iterdir():
    if novel_folder.is_dir():
        all_downloaded_novels.append(get_novel_info(novel_folder))
