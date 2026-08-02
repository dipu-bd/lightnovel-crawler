# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.wpcategory import WpCategoryTemplate

logger = logging.getLogger(__name__)


class OnTimeStoryCrawler(WpCategoryTemplate):
    base_url = ["https://ontimestory.eu/"]

    can_search = True

    chapter_body_selector = ".entry-content"

    # Permalinks keep the `index.php` front controller, so a novel url reads
    # /index.php/category/<slug>/ — the default pattern still finds the slug in it.
    landing_link_selector = ""
