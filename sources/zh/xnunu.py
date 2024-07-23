import logging
from bs4 import Tag
from lncrawl.core.crawler import Crawler

from lncrawl.models import Volume, Chapter

logger = logging.getLogger(__name__)


class Xnunu(Crawler):
    """https://www.xnunu.com crawler, search is behind captcha so not feasible."""

    base_url = ["https://www.xnunu.com/"]

    def initialize(self) -> None:
        # reminder to bookmark that's in every page at the start -> removed.
        self.cleaner.bad_tag_text_pairs["font"] = [
            "提示您：看后求收藏（",
            "搞事马甲不能掉,新努努书坊,www.xnunu.com",
            "），接着再看更方便。"
        ]

    def download_chapter_body(self, chapter: Chapter) -> str:
        main_data = self.get_soup(chapter.url)

        header = main_data.select_one("div#content>.page-header")
        chap_title = header.select_one("h1.h4")
        chap_paging = header.select_one("h1.h4>small")

        # titles in chapter list are not always complete
        # also we don't want a "page x/y" after each chapter's name
        chapter.title = chap_title.text.replace(chap_paging.text, "")

        # some chapters have multiple pages, we want all the content
        # page links look like 123_2 123_3.html, etc.
        def _has_next_page(next_url_tag: Tag) -> bool:
            url = next_url_tag["href"]
            frag = url.split("/")[-1]
            return "_" in frag

        def cleanup_page(page: Tag) -> Tag:
            """
                Get rid of repeating author name at the start of every page
                Thus multiple times per chapter...
            """
            first_child = page.select("p")[0]
            if first_child is not None and first_child.text.startswith(self.novel_author):
                first_child.decompose()
            return page

        curr_page = main_data
        first_page = curr_page.select_one("#chaptercontent")
        chap_data = [cleanup_page(first_page)]

        while _has_next_page(curr_page.select_one("#next_url")):
            curr_page = self.get_soup(self.absolute_url(curr_page.select_one("#next_url")["href"]))
            chap_data.append(cleanup_page(curr_page.select_one("#chaptercontent")))

        return "\n".join([
            self.cleaner.extract_contents(chap) for chap in chap_data
        ])

    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        novel_id = self.novel_url.split("/")[-1]
        try:
            int(novel_id)
        except ValueError:
            logger.error("Couldn't get novel_id from URL, "
                         "URL should look like https://www.xnunu.com/book/9223")
            return

        container = soup.select_one(".book-bookinfo")

        possible_title = container.select_one("h1.name")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = container.select_one("img.thumbnail")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = container.select_one('p>a.btn-info')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        assert self.novel_author, "No novel author, required for cleanup"
        logger.info("Novel Author: %s", self.novel_author)

        possible_tag = soup.select_one('ol.breadcrumb > li:nth-child(2) > a')
        if isinstance(possible_tag, Tag):
            self.novel_tags = [possible_tag.text.strip()]
        logger.info("Novel Tag: %s", self.novel_tags)

        possible_synopsis = container.select_one("#bookIntro")
        if isinstance(possible_synopsis, Tag):
            self.novel_synopsis = possible_synopsis.text
        logger.info("Novel Synopsis: %s", self.novel_synopsis)

        # this is required to be able to fetch chapters if there are > 100 (paginated results)
        chap_overview = self.get_soup(f"https://www.xnunu.com/index/9/{novel_id}/1.html")
        # this will cause the first page to be fetched two times but is more convenient on the code
        dropdown = chap_overview.select_one("#indexselect")  # there's two of these, same content
        chap_links = [self.absolute_url(opt["value"]) for opt in dropdown.select("option")]

        for link in chap_links:
            chap_data = self.get_soup(link)
            chapter_list = chap_data.select("dl.panel-chapterlist>dd>a")

            for a in chapter_list:
                vol_id = len(self.chapters) // 100 + 1
                if len(self.chapters) % 100 == 0:
                    self.volumes.append(Volume(vol_id))
                self.chapters.append(
                    Chapter(
                        len(self.chapters) + 1,
                        url=self.absolute_url(a["href"]),
                        title=a.text.strip(),
                        volume=vol_id,
                    )
                )
