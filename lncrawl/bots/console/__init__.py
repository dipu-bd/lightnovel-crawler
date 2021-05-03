# -*- coding: utf-8 -*-
from typing import Optional
from lncrawl.core.app import App
import logging


class ConsoleBot:
    log = logging.getLogger(__name__)

    def __init__(self) -> None:
        self.app: Optional[App] = None
    # end def

    from .start import start
    from .start import process_chapter_range

    from .get_crawler import get_novel_url
    from .get_crawler import get_crawlers_to_search
    from .get_crawler import choose_a_novel

    from .login_info import get_login_info

    from .output_style import get_output_path
    from .output_style import force_replace_old
    from .output_style import get_output_formats
    from .output_style import should_pack_by_volume

    from .range_selection import get_range_selection
    from .range_selection import get_range_using_urls
    from .range_selection import get_range_using_index
    from .range_selection import get_range_from_volumes
    from .range_selection import get_range_from_chapters
# end class
