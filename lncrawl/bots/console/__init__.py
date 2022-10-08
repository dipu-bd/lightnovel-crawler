import logging
from typing import Optional

from ...core.app import App


class ConsoleBot:
    log = logging.getLogger(__name__)

    def __init__(self) -> None:
        self.app: Optional[App] = None
        self.search_mode = False

    from .get_crawler import (
        choose_a_novel,
        confirm_retry,
        get_crawlers_to_search,
        get_novel_url,
    )
    from .integration import process_chapter_range, start
    from .login_info import get_login_info
    from .output_style import (
        force_replace_old,
        get_output_formats,
        get_output_path,
        should_pack_by_volume,
    )
    from .range_selection import (
        get_range_from_chapters,
        get_range_from_volumes,
        get_range_selection,
        get_range_using_index,
        get_range_using_urls,
    )
