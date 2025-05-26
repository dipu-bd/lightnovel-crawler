import logging
import os
from typing import Dict, List

from ..models.chapter import Chapter

logger = logging.getLogger(__name__)

try:
    import edge_tts
except ImportError:
    logging.fatal("Failed to import edge-tts")

def generate_audio(app, data: Dict[str, List[Chapter]]) -> List[str]:
    pass

def make_mp3s(app, data: Dict[str, List[Chapter]]) -> List[str]:
    from ..core.app import App

    assert isinstance(app, App)

    mp3_files = []
    for volume, chapters in data.items():
        if not chapters:
            continue

        book_title = (app.crawler.novel_title + " " + volume).strip()
        volumes: Dict[int, List[Chapter]] = {}
        for chapter in chapters:
            suffix = chapter.volume or 1
            volumes.setdefault(suffix, []).append(chapter)
        
        images = []
        image_path = os.path.join(app.output_path, "images")
        if os.path.isdir(image_path):
            images = {
                os.path.join(image_path, filename)
                for filename in os.listdir(image_path)
                if filename.endswith(".jpg")
            }

    # TODO: Implement MP3 generation logic
    
    print("Created: %d MsP3 files" % len(mp3_files))
    return mp3_files
