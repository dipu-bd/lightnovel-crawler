# -*- coding: utf-8 -*-
from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wordpress import WordpressTemplate


class AsadaTranslations(WordpressTemplate):
    base_url = "https://asadatranslations.com/"
    chapter_body_selector = "div.text-left"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(["h3"])
        self.cleaner.bad_text_regex.update(
            [
                r"^Translator:",
                r"^Qii",
                r"^Editor:",
                r"^Maralynx",
                r"^Translator and Editor Notes:",
                r"^Support this novel on",
                r"^NU",
                r"^by submitting reviews and ratings or by adding it to your reading list.",
            ]
        )

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:image"]')
        if tag and tag.get("content"):
            novel.cover_url = self.absolute_url(tag["content"])
        else:
            super().parse_cover(soup, novel)
