from lncrawl.core import PageSoup
from lncrawl.templates.novelpub import NovelPubTemplate


class PandaNovelCo(NovelPubTemplate):
    base_url = [
        "https://pandanovel.co/",
    ]

    def get_search_page_soup(self, query: str) -> PageSoup:
        resp = self.scraper.submit_form(
            f"{self.scraper.origin}lnsearchlive",
            data={"inputContent": query},
            headers={
                "referer": f"{self.scraper.origin}search",
            },
        )
        return PageSoup.create(resp)

    # .chapter-content -> #content
    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        return soup.select_one("#content")
