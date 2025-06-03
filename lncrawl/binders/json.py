import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def make_jsons(app, data):
    json_files: List[str] = []
    root_path = Path(app.output_path)
    json_files.append(str(root_path / 'meta.json'))
    for vol in data:
        for chap in data[vol]:
            file_name = "%s.json" % str(chap["id"]).rjust(5, "0")
            file_path = root_path / "json" / file_name
            if file_path.is_file():
                json_files.append(str(file_path))
    print("Discovered: %d json files" % len(json_files))
    return json_files
