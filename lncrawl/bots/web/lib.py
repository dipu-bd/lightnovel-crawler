from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional
import json
from urllib.parse import quote_plus
from pathlib import Path
from ... import constants


class FinishedJob:
    """
    Represent a successfully downloaded novel, or a failed download.
    Replace JobHandler in lib.jobs when JobHandler is destroyed
    """

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
if not LIGHTNOVEL_FOLDER.exists():
    LIGHTNOVEL_FOLDER.mkdir()


@dataclass(init=False)
class _Novel:
    title: str = None
    path: Path = None
    cover: Path = None
    author: str = None
    chapter_count: int = 0
    volume_count: int = 0
    slug: str = None
    first: str = None
    latest: str = None
    summary: str = None
    language : str = 'en'

    def __init__(self, path: Path):
        self.path = path
        self.slug = quote_plus(path.name)

@dataclass(init=False)
class Novel(_Novel):
    """
    Holds information about a novel.
    """
    sources: list['NovelFromSource']
    prefered_source : 'NovelFromSource' = None
    source_count: int = 0
    search_words: List[str] 

    def __init__(self, path: Path):
        self.search_words = []
        self.sources = []
        super().__init__(path)


@dataclass(init=False)
class NovelFromSource(_Novel):
    """
    Hold information about a novel from a source.
    """
    novel: Novel


def get_novel_info(novel_folder: Path)->Novel:
    """
    Collects information about a novel locally.
    source isn't specified, so we need to find a source that has sufficient 
        metadata for the novel and set it to prefered_source.
    Metadata are randomly picked from the sources.
    """

    novel = Novel(novel_folder.absolute())

    language = set()

    for source_folder in novel_folder.iterdir():
        source = get_source_info(source_folder)
        source.novel = novel
         
        if not novel.cover and source.cover:
            novel.cover = source.cover
            novel.prefered_source = source

        if not novel.author and source.author:
            novel.author = source.author

        if not novel.chapter_count and source.chapter_count:
            novel.chapter_count = source.chapter_count

        if not novel.latest and source.latest:
            novel.latest = source.latest
        
        if not novel.first and source.first:
            novel.first = source.first

        if not novel.volume_count and source.volume_count:
            novel.volume_count = source.volume_count

        if not novel.title and source.title:
            novel.title = source.title

        if not novel.summary and source.summary:
            novel.summary = source.summary
        
        if source.language:
            language.add(source.language)
        
        novel.sources.append(source)

    novel.language = ", ".join(language)

    if not novel.title:
        novel.title = novel_folder.name
    novel.source_count = len(novel.sources)
    novel.search_words = sanitize(novel.title + " " + novel.author).split(" ") 
    return novel


def get_source_info(source_folder: Path) -> NovelFromSource:
    """
    Collects information about a novel for a source.
    Source is specified, so we can just read the meta.json file...
    """
    source = NovelFromSource(source_folder.absolute())
    source.cover = (
        f"{source_folder.parent.name}/{source_folder.name}/cover.jpg"
        if (source_folder / "cover.jpg").exists()
        else None
    )
    if (source_folder / "meta.json").exists():
        with open(source_folder / "meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

        try :
            source.latest = meta["chapters"][-1]["title"]
        except KeyError:
            source.latest = None
        try :
            source.first = meta["chapters"][0]["title"]
        except KeyError:
            source.first = None
        source.author = meta["author"] if "author" in meta else None
        source.chapter_count = len(meta["chapters"]) if "chapters" in meta else None
        source.volume_count = len(meta["volumes"]) if "volumes" in meta else None
        source.title = meta["title"] if "title" in meta else source_folder.parent.name
        source.language = meta["language"] if "language" in meta else 'en'
        source.summary = meta["summary"] if "summary" in meta else None
        source.language = meta["language"] if "language" in meta else None

    return source


import unicodedata


def sanitize(text: str) -> str:
    """
    Remove all special characters from a string, replace accentuated characters with their
    non-accentuated counterparts, and remove all non-alphanumeric characters.
    """
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ").upper().strip()
    text = unicodedata.normalize("NFKD", text)
    return "".join([c for c in text if not unicodedata.combining(c)])

@lru_cache
def findSourceWithPath(novel_and_source_path: Path) -> NovelFromSource|None:
    """
    Find the NovelFromSource object corresponding to the path
    """
    novel = None
    for n in all_downloaded_novels:
        if novel_and_source_path.parent == n.path:
            novel = n
            break
    if not novel :
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
        all_downloaded_novels.append(get_novel_info(novel_folder))
