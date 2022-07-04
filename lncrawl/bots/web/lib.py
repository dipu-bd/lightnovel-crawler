from __future__ import annotations
from typing import List
from pathlib import Path
import json
from ... import constants
from .Novel import Novel
from . import database
from . import read_novel_info


LIGHTNOVEL_FOLDER = Path(constants.DEFAULT_OUTPUT_PATH)
if not LIGHTNOVEL_FOLDER.exists():
    LIGHTNOVEL_FOLDER.mkdir()

config_file = Path("lncrawl/bots/web/config.json")
if not config_file.exists():
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump({"host": "localhost", "port":"5000", "website_url":"localhost:5000"}, f, indent=4)
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

WEBSITE_URL = config["website_url"]
HOST = config["host"]
PORT = config["port"]
WEBSITE_URL = WEBSITE_URL.strip("/")


database.all_downloaded_novels: List[Novel] = []
for novel_folder in LIGHTNOVEL_FOLDER.iterdir():
    if novel_folder.is_dir():
        database.all_downloaded_novels.append(read_novel_info.get_novel_info(novel_folder))

database.all_downloaded_novels.sort(key=lambda n: n.clicks, reverse=True)
for i, n in enumerate(database.all_downloaded_novels, start=1):
    n.rank = i

import threading, time
def update_novels_stats():
    """Periodic function to update each novels stats"""
    while True:
        time.sleep(600) # 10 minutes
        for novel in database.all_downloaded_novels:
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
