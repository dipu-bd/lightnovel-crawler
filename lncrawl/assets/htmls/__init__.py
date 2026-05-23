from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).parent


@lru_cache
def loading_path() -> Path:
    return ROOT / "loading.html"


@lru_cache
def loading_html() -> str:
    return loading_path().read_text()
