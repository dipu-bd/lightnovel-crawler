# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from lncrawl.core import SoupTemplate

logger = logging.getLogger(__name__)


class GravityTalesCrawler(SoupTemplate):
    base_url = "https://gravitytales.com/"
    has_mtl = True
    can_search = True

    search_item_list_selector = "li.card._story"
    search_item_title_selector = "h3.card__title"
    search_item_url_selector = "h3.card__title a"

    novel_title_selector = "article h1"
    novel_author_selector = ".author"

    chapter_list_selector = "#chapter-sections-wrapper li.chapter-group__list-item a"
    chapter_body_selector = ".chapter__content"

    def build_search_url(self, query: str) -> str:
        return f"https://gravitytales.com/?s={quote_plus(query)}"
