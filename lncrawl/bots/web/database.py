from typing import List
from .Novel import Novel

all_downloaded_novels: List[Novel] = []

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .downloader.Job import JobHandler, FinishedJob

    jobs: dict[str, FinishedJob | JobHandler]
    
jobs = {}