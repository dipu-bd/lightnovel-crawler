import logging
from typing import Generator, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, Volume
from lncrawl.templates.soup.general import GeneralSoupTemplate

logger = logging.getLogger(__name__)


class WtrLabCrawler(GeneralSoupTemplate):
    base_url = ["https://wtr-lab.com/en",
                "http://wtr-lab.com/en",
                "https://www.wtr-lab.com/en",
                "http://www.wtr-lab.com/en",
                "https://wtr-lab.com",
                "http://wtr-lab.com"]

    def initialize(self) -> None:
        logger.info("Initializing WtrLabCrawler")

    def get_novel_soup(self) -> BeautifulSoup:
        return self.get_soup(self.novel_url)

    def parse_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find("a", class_="title")
        if not title_tag:
            raise ValueError("Title not found on the page.")
        return title_tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        cover_tag = soup.find("a", class_="image-wrap").find("img")
        if not cover_tag or not cover_tag.get("src"):
            raise ValueError("Cover image not found on the page.")
        return cover_tag["src"].strip()

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        author_tag = soup.find("div", class_="author-wrap")
        if not author_tag:
            raise ValueError("Author information not found on the page.")
        author_link = author_tag.find("a")
        if author_link:
            yield author_link.text.strip()
        else:
            yield "Unknown Author"

    def parse_chapter_list(
    self, soup: BeautifulSoup
) -> Generator[Union[Chapter, Volume], None, None]:
    # Locate the chapter list container
    chapters_section = soup.find("div", class_="chapter-list")
    if not chapters_section:
        logger.error("Chapter list not found on the page.")
        raise ValueError("Chapter list not found on the page.")
    
    # Initialize volume
    volume_id = 1
    volume = Volume(id=volume_id, title=f"Volume {volume_id}")
    yield volume

    # Parse chapters
    for chapter_tag in chapters_section.find_all("a", class_="chapter-item"):
        chapter_title = chapter_tag.find("span").text.strip()
        chapter_url = self.absolute_url(chapter_tag["href"])

        # Generate Chapter object
        chapter = Chapter(
            id=len(self.chapters) + 1,
            title=chapter_title,
            url=chapter_url,
            volume=volume_id,
        )
        yield chapter


    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        chapter_body = soup.find("div", class_="chapter-content")
        if not chapter_body:
            raise ValueError("Chapter content not found on the page.")
        return chapter_body

    def login(self, username_or_email: str, password_or_token: str) -> None:
        logger.info("Login method not implemented for WtrLabCrawler")

    def logout(self):
        logger.info("Logout method not implemented for WtrLabCrawler")
