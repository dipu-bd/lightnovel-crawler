import logging

from bs4 import BeautifulSoup, Tag

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class Luminarynovels(MadaraTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://luminarynovels.com/"]

    def initialize(self) -> None:
        # contains self-promo and discord link
        self.cleaner.bad_css.add("div.chapter-warning.alert.alert-warning")

    def select_chapter_tags(self, soup: BeautifulSoup):
        try:
            clean_novel_url = self.novel_url.split("?")[0].strip("/")
            response = self.submit_form(f"{clean_novel_url}/ajax/chapters/", retry=0)
            soup = self.make_soup(response)
            chapters = soup.select(" div.page-content-listing.single-page > div > ul > li > a")
            if not chapters:
                raise Exception("No chapters on first URL")
        except Exception:
            nl_id = soup.select_one("#manga-chapters-holder[data-id]")
            assert isinstance(nl_id, Tag)
            response = self.submit_form(
                f"{self.home_url}wp-admin/admin-ajax.php",
                data={
                    "action": "manga_get_chapters",
                    "manga": nl_id["data-id"],
                },
            )
            soup = self.make_soup(response)
            chapters = soup.select("ul.main .wp-manga-chapter a")

        yield from reversed(chapters)
