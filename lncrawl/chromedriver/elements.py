import logging
from enum import Enum
from typing import List, Union

from bs4 import Tag

from ..core.soup import SoupMaker

logger = logging.getLogger(__name__)

try:
    from selenium.webdriver.remote.webelement import WebElement as _WebElement
    from selenium.webdriver.support.relative_locator import RelativeBy
    import selenium.webdriver.support.expected_conditions as EC
except ImportError:
    logger.error("`selenium` is not found")

__all__ = [
    "EC",
    "By",
    "RelativeBy",
    "WebElement",
]


# from selenium.webdriver.common.by import By
class By(str, Enum):
    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"

    def __str__(self) -> str:
        return self.value


class WebElement(_WebElement):
    def __init__(self, parent, id_):
        super().__init__(parent, id_)

    @property
    def __soup_maker(self) -> SoupMaker:
        if hasattr(self._parent, "soup_maker"):
            maker = getattr(self._parent, "soup_maker")
            if isinstance(maker, SoupMaker):
                return maker
        return SoupMaker()

    def inner_html(self) -> str:
        return self.get_attribute("innerHTML")

    def outer_html(self) -> str:
        return self.get_attribute("outerHTML")

    def as_tag(self) -> Tag:
        html = self.outer_html()
        if not hasattr(self, "_tag") or self._html != html:
            self._html = html
            self._tag = self.__soup_maker.make_tag(self._tag)
        return self._tag

    def find_all(
        self, selector: str, by: Union[By, RelativeBy] = By.CSS_SELECTOR
    ) -> List["WebElement"]:
        if isinstance(by, By):
            by = str(by)
        self.find_elements(by, selector)

    def find(
        self, selector: str, by: Union[By, RelativeBy] = By.CSS_SELECTOR
    ) -> "WebElement":
        if isinstance(by, By):
            by = str(by)
        self.find_element(by, selector)
