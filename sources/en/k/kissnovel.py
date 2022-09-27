# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class KissNovelCrawler(Crawler):
    base_url = "https://kiss-novel.com/"

    # FIXME: Tried getting search to work, but it uses a autocomplete function and I can't figure out how to get results from it.
    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = " ".join(
            [str(x) for x in soup.select_one(".post-title h1").contents if not x.name]
        ).strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".summary_image img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        author = soup.find("div", {"class": "author-content"}).findAll("a")
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        else:
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        latest_chapter = soup.select("div.post-content_item ul li a")[0].text
        chapter_count = [int(i) for i in latest_chapter.split() if i.isdigit()]
        page_count = (chapter_count)[0] // 10 + 1
        chapters_page_url = "%s/%s#chapter-section"

        chapters = []

        for i in range(page_count):
            url = chapters_page_url % (self.novel_url, str(i + 1))
            logger.debug("Visiting %s", url)
            soup = self.get_soup(url)
            chapters.extend(soup.select("ul.main li.wp-manga-chapter a"))
        chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            if len(self.chapters) % 100 == 0:
                vol_title = "Volume " + str(vol_id)
                self.volumes.append(
                    {
                        "id": vol_id,
                        "title": vol_title,
                    }
                )
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select("div.reading-content p")

        body = [str(p) for p in contents if p.text.strip()]
        return "<p>" + "</p><p>".join(body) + "</p>"

        # if contents.h3:
        #    contents.h3.extract()

        # for codeblock in contents.findAll('div', {'class': 'code-block'}):
        #    codeblock.extract()

        # return str(contents)
