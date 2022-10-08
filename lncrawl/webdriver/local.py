# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2
# https://github.com/ultrafunkamsterdam/undetected-chromedriver

import json
import locale
import logging
import os
from threading import Lock
from typing import Optional

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Remote as WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER

from ..core.exeptions import LNException
from ..core.soup import SoupMaker
from ..utils.platforms import Platform, Screen
from .elements import WebElement, _add_virtual_authenticator
from .queue import _acquire_queue, _release_queue
from .scripts import _override_get

logger = logging.getLogger(__name__)


try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    logger.warn("`webdriver-manager` is not found")

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

    if not Platform.display:
        headless = True

    # Configure window behavior
    if headless:
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
    else:
        width = int(max(640, Screen.view_width * 2 / 3))
        height = int(max(480, Screen.view_height * 2 / 3))
        options.add_argument(f"--window-size={width},{height}")

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
    options.set_capability("quietExceptions", True)

    # Chrome specific options
    options.accept_insecure_certs = True
    options.unhandled_prompt_behavior = "dismiss"
    options.strict_file_interactability = False
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if not is_debug:
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Configure user data dir
    if user_data_dir and os.access(user_data_dir, mode=os.F_OK):
        user_data_dir = os.path.normpath(os.path.abspath(user_data_dir))
        options.add_argument(f"--user-data-dir={user_data_dir}")
    try:
        prefs_path = os.path.join(user_data_dir, "Default", "Preferences")
        with open(prefs_path, encoding="latin1", mode="r+") as fp:
            cfg = json.load(fp)
            cfg["profile"]["exit_type"] = None
            fp.seek(0, 0)
            json.dump(cfg, fp)
            logger.debug("Cleared exit_type flag")
    except Exception as e:
        logger.debug("Could not clear any bad exit_type flag | %s", e)

    try:
        executable_path = _acquire_chrome_driver_path()
        logger.debug(
            "Creating chrome instance | "
            + f"headless={headless} | "
            + f"driver_path={executable_path}"
        )
        chrome = Chrome(
            executable_path=executable_path,
            options=options,
        )
    except Exception as e:
        logger.exception("Failed to create chrome instance", e)
        chrome = None

    if not chrome:
        raise LNException("Could not obtain a webdriver")

    logger.info("Created chrome instance > %s", chrome.session_id)
    chrome.set_window_position(0, 0)

    if not soup_maker:
        soup_maker = SoupMaker()
    chrome._soup_maker = soup_maker
    chrome._web_element_cls = WebElement

    _add_virtual_authenticator(chrome)
    _override_get(chrome)
    _release_queue(chrome)

    return chrome
