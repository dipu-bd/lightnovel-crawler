# -*- coding: utf-8 -*-
import logging
import re

from bs4.element import Tag
from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume, Chapter

logger = logging.getLogger(__name__)

volume_aliases = {"volume", "arc", "series", "saga", "chronicle", "tome", "storyline"}


class NYXTranslation(Crawler):
    base_url = ["https://nyx-translation.com/", "https://nyxtranslation.home.blog/"]
    has_manga = False
    has_mtl = False

    def initialize(self):
        self.cleaner.bad_tags.add("script")
        self.cleaner.bad_tags.add("a")

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        content = soup.select_one("main#main > article")

        entry_title = content.select_one("h1.entry-title")
        assert isinstance(entry_title, Tag)
        self.novel_title = entry_title.text.strip()
        pre_tags = content.find("strong", text=re.compile(r"Genre.*:.*"))
        if pre_tags:
            tags = pre_tags.find_next_sibling(None, text=re.compile(r"\w+,"))
            for tag in tags.split(", "):
                self.novel_tags.append(tag)

        pre_author = content.find("strong", text=re.compile(r"Author.*:?.*"))
        if pre_author:
            maybe_author = pre_author.next_sibling
            author = maybe_author
            if ": " in maybe_author.text:
                author = maybe_author.next_sibling
            self.novel_author = author.text

        cover = content.select_one("img")  # first image is the novel cover
        if cover:
            src = str(cover['src'])
            # may be replaced with JS after load, in such case try and get the real img hidden in data-values
            if src.startswith("data:"):
                try:
                    src = cover["data-orig-file"]
                except KeyError:
                    pass
            self.novel_cover = self.absolute_url(src)

        description = ""
        description_start = content.find("p", text="Description")
        d_next = description_start.next_sibling
        while True:
            if not isinstance(d_next, Tag):
                d_next = d_next.next_sibling
                continue
            if "Alternative Name(s)" in d_next.next_sibling or d_next.name != "p":
                break
            description += d_next.text + "\n"
            d_next = d_next.next_sibling
        self.novel_synopsis = description

        # "inconsistency is key" - the site author, probably... (s is optional)
        chapters_start = content.find("p", text=re.compile(r"Table of Contents?", re.IGNORECASE))
        c_next = chapters_start.next_sibling
        chap = ""
        while c_next:
            if not isinstance(c_next, Tag):
                c_next = c_next.next_sibling
                continue

            # there are some aria-hidden spacing divs within the chapter list
            # also skip text-emtpy elements
            if (c_next.name == "div" and c_next.has_attr("aria-hidden")) or not c_next.text:
                c_next = c_next.next_sibling
                continue
            links = c_next.find_all("a")
            if not links:
                if self.is_volume(c_next.text):
                    logger.info("Found a volume: %s", c_next.text)
                    self.volumes.append(
                        Volume(
                            id=len(self.volumes) + 1,
                            title=c_next.text.strip().replace(":", ""),
                        )
                    )
                else:
                    # these are all elements (except the spacer div) that shouldn't appear -> it should be done
                    if c_next.name in ["div", "script", "footer"]:
                        break
                    chap = c_next.text  # would be a chapter title
            else:
                for link in links:
                    href = str(link["href"])
                    if not self.on_site(href):
                        logger.info("Found external link, assuming lazy structure, link: %s", href)
                        c_next = chapters_start.parent.next_sibling
                        break  # break out of for loop in this case.
                    if not re.match(re.compile(r".+-part-\d+.*"), href.lower()):
                        chap = ""
                    self.chapters.append(
                        Chapter(
                            id=len(self.chapters) + 1,
                            title=f"{chap} {link.text.lower()}",
                            url=self.absolute_url(href),
                            # guarantee chapters like prologues listed outside vol1, are in vol1
                            volume=max(len(self.volumes), 1),
                        )
                    )
            c_next = c_next.next_sibling

        # in rare cases the volume names don't have any indicators, so we end up without any, this "fixes" that.
        if not self.volumes:
            self.volumes.append(
                Volume(
                    id=1,
                    title="All content"
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)

        contents_html = soup.select_one("div.entry-content")
        return self.cleaner.extract_contents(contents_html)

    def on_site(self, href: str) -> bool:
        if "http" in href.lower():
            return max([href.startswith(url) for url in self.base_url])
        return False

    @classmethod
    def is_volume(cls, text: str) -> bool:
        return bool(max([x in text.lower() for x in volume_aliases]))
