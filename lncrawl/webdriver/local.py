# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2
# https://github.com/ultrafunkamsterdam/undetected-chromedriver

import locale
import logging
import os
from threading import Lock
from typing import Optional

from selenium.webdriver import Remote as WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
from undetected_chromedriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from ..core.soup import SoupMaker
from ..utils.platforms import Screen, has_display
from .elements import WebElement
from .job_queue import _acquire_queue, _release_queue

logger = logging.getLogger(__name__)


__installer_lock = Lock()


def _acquire_chrome_driver_path():
    with __installer_lock:
        return ChromeDriverManager().install()


def create_local(
    options: Optional["ChromeOptions"] = None,
    timeout: Optional[float] = None,
    headless: bool = True,
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

    if not has_display():
        headless = True

    # Set default language
    try:
        language = locale.getdefaultlocale()[0].replace("_", "-")
    except Exception:
        pass
    options.add_argument("--lang=%s" % (language or "en-US"))

    # Logging configs
    LOGGER.setLevel(logging.WARN)
    options.add_argument(f"--log-level={0 if is_debug else 3}")
    if not is_debug:
        LOGGER.setLevel(1000)

    # Suppress bothersome stuffs
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-first-run")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--disable-dev-shm-usage")

    # Add capabilities
    #options.set_capability("quietExceptions", True)
    options.set_capability("acceptInsecureCerts", True)
    #options.set_capability("useAutomationExtension", False)

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

    # Chrome specific experimental options
    options.accept_insecure_certs = True
    options.unhandled_prompt_behavior = "dismiss"
    options.strict_file_interactability = False
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # if not is_debug:
    #     options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # # Set remote debuging host and port
    # debug_host = "127.0.0.1"
    # debug_port = free_port(debug_host)
    # options.add_argument(f"--remote-debugging-host={debug_host}")
    # options.add_argument(f"--remote-debugging-port={debug_port}")
    # options.debugger_address = f"{debug_host}:{debug_port}"

    executable_path = _acquire_chrome_driver_path()
    logger.debug(
        "Creating chrome instance | "
        + f"headless={headless} | "
        + f"driver_path={executable_path}"
    )
    chrome = Chrome(
        driver_executable_path=executable_path,
        options=options,
        desired_capabilities=options.to_capabilities(),
        keep_alive=True,
        user_data_dir=user_data_dir,
        headless=headless,
    )
    logger.info("Created chrome instance > %s", chrome.session_id)
    chrome.set_window_position(0, 0)

    if not soup_maker:
        soup_maker = SoupMaker()
    chrome._soup_maker = soup_maker
    chrome._web_element_cls = WebElement

    # _add_virtual_authenticator(chrome)
    # _override_get(chrome)

    _release_queue(chrome)
    return chrome
