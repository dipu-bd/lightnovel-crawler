# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.wpcategory import WpCategoryTemplate

logger = logging.getLogger(__name__)


class SammyAndPassionCrawler(WpCategoryTemplate):
    base_url = ["https://sammyandpassion.com/"]

    can_search = True

    chapter_body_selector = ".entry-content"

    landing_link_selector = ""
