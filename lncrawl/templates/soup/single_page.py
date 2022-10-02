from typing import Generator

from bs4 import BeautifulSoup

from .paginated_toc import PaginatedSoupTemplate


class SinglePageSoupTemplate(PaginatedSoupTemplate):
    is_template = True

    def generate_page_soups(
        self, soup: BeautifulSoup
    ) -> Generator[BeautifulSoup, None, None]:
        yield soup
