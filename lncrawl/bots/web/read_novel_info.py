import json
from .Novel import Novel, NovelFromSource
from pathlib import Path
import shutil

def get_novel_info(novel_folder: Path) -> Novel:
    """
    Collects information about a novel locally.
    source isn't specified, so we need to find a source that has sufficient
        metadata for the novel and set it to prefered_source.
    Metadata are randomly picked from the sources.
    """

    novel = Novel(novel_folder.absolute())

    # --------------------------------------------------------------------------
    language: set[str] = set()

    for source_folder in novel_folder.iterdir():
        if not source_folder.is_dir():
            continue
        
        source = _get_source_info(source_folder)
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
    
    
    # --------------------------------------------------------------------------
    

    novel_stats_file = Path(novel_folder / "stats.json")

    if not novel_stats_file.exists():
        shutil.copy(str(Path(__file__).parent / "_stats.json"), str(novel_stats_file))

    with open(novel_stats_file, "r", encoding="utf-8") as f:
        novel_stats = json.load(f)
        novel.clicks = novel_stats["clicks"]
        novel.ratings = novel_stats["ratings"]

    novel.overall_rating = sum(novel.ratings.values()) / len(novel.ratings)
    
    return novel


def _get_source_info(source_folder: Path) -> NovelFromSource:
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

        try:
            source.latest = meta["chapters"][-1]["title"]
        except KeyError:
            source.latest = ""
        try:
            source.first = meta["chapters"][0]["title"]
        except KeyError:
            source.first = ""
        source.author = meta["author"] if "author" in meta else ""
        source.chapter_count = len(meta["chapters"]) if "chapters" in meta else 0
        source.volume_count = len(meta["volumes"]) if "volumes" in meta else 0
        source.title = meta["title"] if "title" in meta else source_folder.parent.name
        source.language = meta["language"] if "language" in meta else "en"

        source.summary = meta["summary"] if "summary" in meta else ""

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
