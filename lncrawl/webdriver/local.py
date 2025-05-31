# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2
# https://github.com/ultrafunkamsterdam/undetected-chromedriver

import logging
import os
from typing import Optional

from selenium.webdriver import Remote as WebDriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.remote.remote_connection import LOGGER

from ..core.soup import SoupMaker
from ..utils.platforms import Screen, Platform
from .elements import WebElement
from .job_queue import _acquire_queue, _release_queue
from .scripts import _override_get

logger = logging.getLogger(__name__)


def create_local(
    options: Optional["ChromeOptions"] = None,
    timeout: Optional[float] = None,
    headless: bool = False,
    user_data_dir: Optional[str] = None,
    soup_maker: Optional[SoupMaker] = None,
    **kwargs,
) -> WebDriver:
    """
    Acquire a webdriver instane. There is a limit of how many webdriver
    instances you can keep open at a time. You must call quit() to cleanup
    existing one to obtain new ones.

    NOTE: You must call quit() to cleanup the queue.
    """
    _acquire_queue(timeout)
    is_debug = os.getenv("debug_mode")

    if not options:
        options = ChromeOptions()

    if not headless and not Platform.has_display:
        headless = True

    # Options for chrome driver
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-first-run")
    options.add_argument("--lang=en-US")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-blink-features=AutomationControlled")

    #  options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--disable-popup-blocking")

    # Logging configs
    LOGGER.setLevel(logging.WARN)
    options.add_argument(f"--log-level={0 if is_debug else 3}")
    if not is_debug:
        LOGGER.setLevel(1000)

    # Configure window behavior
    if headless:
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
    else:
        width = max(640, Screen.view_width * 3 // 4)
        height = max(480, Screen.view_height * 3 // 4)
        width = int(os.getenv("CHROME_WIDTH", width))
        height = int(os.getenv("CHROME_HEIGHT", height))
        options.add_argument(f"--window-size={width},{height}")

    # # Set remote debuging host and port
    # debug_host = "127.0.0.1"
    # debug_port = free_port(debug_host)
    # options.add_argument(f"--remote-debugging-host={debug_host}")
    # options.add_argument(f"--remote-debugging-port={debug_port}")
    # options.debugger_address = f"{debug_host}:{debug_port}"

    # Add capabilities
    options.set_capability("acceptInsecureCerts", True)
    # options.set_capability("quietExceptions", True)

    # Chrome specific experimental options
    options.accept_insecure_certs = True
    options.strict_file_interactability = False
    options.unhandled_prompt_behavior = "dismiss"
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # initialize instance
    chrome = Chrome(
        options=options,
        keep_alive=True,
    )
    logger.info("Created chrome instance > %s", chrome.session_id)
    chrome.set_window_position(0, 0)

    if not soup_maker:
        soup_maker = SoupMaker()
    chrome._soup_maker = soup_maker
    chrome._web_element_cls = WebElement

    # _add_virtual_authenticator(chrome)
    _override_get(chrome)

    _release_queue(chrome)
    return chrome
