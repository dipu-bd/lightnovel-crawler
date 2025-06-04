import logging
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)


def make_jsons(app, data) -> Generator[str, None, None]:
    root_path = Path(app.output_path)
    yield str(root_path / 'meta.json')
    for vol in data:
        for chap in data[vol]:
            file_name = "%s.json" % str(chap["id"]).rjust(5, "0")
            file_path = root_path / "json" / file_name
            if file_path.is_file():
                yield str(file_path)
