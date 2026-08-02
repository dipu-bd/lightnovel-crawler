# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.wpcategory import WpCategoryTemplate

logger = logging.getLogger(__name__)


class EatApplePiesCrawler(WpCategoryTemplate):
    base_url = ["https://eatapplepies.com/"]

    can_search = True

    chapter_body_selector = ".entry-content"

    landing_link_selector = ""
