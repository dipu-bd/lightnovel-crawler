from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).parent


@lru_cache
def epub_style_css() -> bytes:
    return (ROOT / "style.css").read_bytes()


@lru_cache
def epub_cover_xhtml() -> bytes:
    return (ROOT / "cover.xhtml").read_bytes()


@lru_cache
def epub_chapter_xhtml() -> bytes:
    return (ROOT / "chapter.xhtml").read_bytes()
