from pathlib import Path

IMAGES_DIR = Path(__file__).parent


def favicon_icon() -> Path:
    """
    Returns the path to the favicon.ico image file.
    """
    return IMAGES_DIR / "favicon.ico"


def lncrawl_icon() -> Path:
    """
    Returns the path to the lncrawl.ico image file.
    """
    return IMAGES_DIR / "lncrawl.ico"
