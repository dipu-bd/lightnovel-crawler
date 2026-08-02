# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.blogger import BloggerLabelTemplate

logger = logging.getLogger(__name__)


class TurkceNovelOkuCrawler(BloggerLabelTemplate):
    base_url = ["https://turkcenoveloku.blogspot.com/"]
    language = "tr"

    can_search = True

    # A custom reader theme rather than Blogger's stock one, so the post body is not where
    # the other blogs keep it.
    chapter_body_selector = ".text-content"
