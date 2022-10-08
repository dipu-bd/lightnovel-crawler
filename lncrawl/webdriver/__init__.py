# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2
# https://github.com/ultrafunkamsterdam/undetected-chromedriver

import logging
from typing import Optional

from selenium.webdriver import ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver

from ..core.arguments import get_args
from ..core.soup import SoupMaker
from .local import create_local
from .remote import create_remote

logger = logging.getLogger(__name__)


def create_new(
    options: Optional["ChromeOptions"] = None,
    timeout: Optional[float] = None,
    user_data_dir: Optional[str] = None,
    soup_maker: Optional[SoupMaker] = None,
    headless: bool = True,
    **kwargs,
) -> WebDriver:
    args = get_args()
    if args.selenium_grid:
        return create_remote(
            address=args.selenium_grid,
            options=options,
            timeout=timeout,
            soup_maker=soup_maker,
        )
    else:
        return create_local(
            options=options,
            timeout=timeout,
            soup_maker=soup_maker,
            user_data_dir=user_data_dir,
            headless=headless,
        )
