# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2
# https://github.com/ultrafunkamsterdam/undetected-chromedriver

import json
import locale
import logging
import os
from threading import Lock
from typing import Optional

from selenium.webdriver import Remote as WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER

from .scripts import _override_get
from ..core.exeptions import LNException
from ..core.soup import SoupMaker
from ..utils.platforms import Platform, Screen
from .elements import WebElement, _add_virtual_authenticator
from .job_queue import _acquire_queue, _release_queue

logger = logging.getLogger(__name__)

try:
    # For Python 3.7+
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    logger.warn("`webdriver-manager` is not found")

try:
    from undetected_chromedriver import Chrome, ChromeOptions

    using_undetected_chromedriver = True
except Exception:
    logger.warn("Could not use `undetected_chromedriver`")
    from selenium.webdriver import Chrome, ChromeOptions

    using_undetected_chromedriver = False


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
    options.set_capability("quietExceptions", True)
    options.set_capability("acceptInsecureCerts", True)
    options.set_capability("useAutomationExtension", False)

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

    # Chrome specific experimental options
    options.accept_insecure_certs = True
    options.unhandled_prompt_behavior = "dismiss"
    options.strict_file_interactability = False
    if not using_undetected_chromedriver:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if not is_debug:
            options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Configure user data dir
    if not using_undetected_chromedriver:
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

    # # Set remote debuging host and port
    # debug_host = "127.0.0.1"
    # debug_port = free_port(debug_host)
    # options.add_argument(f"--remote-debugging-host={debug_host}")
    # options.add_argument(f"--remote-debugging-port={debug_port}")
    # options.debugger_address = f"{debug_host}:{debug_port}"

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
            desired_capabilities=options.to_capabilities(),
            keep_alive=True,
            user_data_dir=user_data_dir,
            headless=headless,
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

    if not using_undetected_chromedriver:
        _add_virtual_authenticator(chrome)
        _override_get(chrome)

    _release_queue(chrome)
    return chrome
