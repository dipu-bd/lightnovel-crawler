import logging
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, Volume
from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class Novel_Bin(NovelFullTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://novel-bin.com/", "https://novelbin.me"]
    request_rate_limit = 1

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        # The whole list is on the novel page now, in order and unpaginated. The inherited
        # ajax route still exists but keys on a numeric novel id this site no longer emits —
        # `data-novel-id` holds the slug — so asking for it returns nothing.
        #
        # Not the inherited selector: its `select > option[value]` half also matches the
        # theme-colour picker, which contributes forty entries named "Light gray".
        anchors = tag.select("ul.list-chapter > li > a[href]")
        if anchors:
            return anchors
        return super().select_chapter_tags(tag, novel, volume)
