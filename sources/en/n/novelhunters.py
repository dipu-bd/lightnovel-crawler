# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class NovelHunters(WordpressTemplate):
    base_url = 'https://www.novelhunters.com/'
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(
            [
                "a",
                "h3",
            ]
        )
        self.cleaner.bad_css.update(
            [
                ".code-block",
                ".adsbygoogle",
                ".adsense-code",
                ".sharedaddy",
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                "*** Can’t wait until tomorrow to see more? Want to show your support? "
                + "to read premium additional chapters ahead of time!",
                "[T/N Note: To Get more Free chapters Quickly Support us on",
                ". For more and better novels updates. If you have any suggestions, "
                + "please give it on the comment box or contact us on",
            ]
        )
