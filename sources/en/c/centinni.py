# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class Centinni(WordpressTemplate):
    base_url = "https://www.centinni.com/"
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(
            [
                "ah3",
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                r"^Link for previous chapters:",
                r"^https://www.novelupdates.com/series/possessing-nothing/",
                r"^This translation belongs to Centinni.",
                r"^https://discord.gg/aqDszgB",
                r"^Hey guys, join us now on our discord server:",
                r"^https://www.paypal.me/centinni1",
                r"^You may also donate through paypal to support the people who work on "
                + "these novels (please specify which novel you are supporting):",
                r"^. And get a chance to chat with your favorite translators and editors."
                + " Meet more like-minded people and have a fun time with real-time novel "
                + "updates and much more.",
                r"^You may also donate through paypal to support the people who work on these"
                + " novels (please specify which novel you are supporting):",
                r"^You can donate on Ko-fi(from main page) Extra chapter be released when"
                + " 10$/chapter have been slowly accumulated on Ko-fi. Please mention the "
                + "novel you are supporting.",
                r"^Centinni is translating this novel.",
                r"^Possessing Nothing now has a chat channel! Join our discord server to "
                + "chat with your team and more friends!",
            ]
        )
