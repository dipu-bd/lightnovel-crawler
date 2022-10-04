# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2
# https://github.com/ultrafunkamsterdam/undetected-chromedriver

import atexit
import json
import locale
import logging
import os
from threading import Lock, Semaphore
from typing import List, Optional

from ..core.exeptions import LNException
from ..utils.platforms import Platform, Screen
from . import scripts

logger = logging.getLogger(__name__)

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    logger.warn("`webdriver-manager` is not found")

try:
    import selenium.webdriver.support.expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.remote.command import Command
    from selenium.webdriver.remote.remote_connection import LOGGER
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.webdriver.support.wait import WebDriverWait

    LOGGER.setLevel(logging.ERROR)
except ImportError:
    logger.error("`selenium` is not found")


__all__ = [
    "By",
    "EC",
    "Command",
    "WebElement",
    "WebDriverWait",
    "create_chrome",
]


MAX_BROWSER_INSTANCES = 8

__installer_lock = Lock()
__open_browsers: List[WebDriver] = []
__semaphore = Semaphore(MAX_BROWSER_INSTANCES)


def __get_driver_path():
    with __installer_lock:
        return ChromeDriverManager().install()


def cleanup():
    for chrome in __open_browsers:
        chrome.quit()


atexit.register(cleanup)


def __override_quit(chrome: WebDriver):
    original = chrome.quit

    def override(*args, **kwargs):
        if chrome in __open_browsers:
            __semaphore.release()
            __open_browsers.remove(chrome)
            logger.info("Destroyed instance: %s", chrome.session_id)
        original(*args, **kwargs)

    chrome.quit = override


def __override_get(chrome: WebDriver):
    original = chrome.get

    def override(*args, **kwargs):
        if chrome.execute_script(scripts.return_webdriver_script):
            logger.info("patch navigator.webdriver")
            chrome.execute_cdp_cmd(
                scripts.add_script_to_evaluate_on_new_document,
                {"source": scripts.hide_webdriver_from_navigator_script},
            )
            logger.info("patch user-agent string")
            user_agent = chrome.execute_script(scripts.return_user_agent_script)
            chrome.execute_cdp_cmd(
                scripts.set_user_agent_override,
                {"userAgent": user_agent.replace("Headless", "")},
            )
            chrome.execute_cdp_cmd(
                scripts.add_script_to_evaluate_on_new_document,
                {"source": scripts.override_touch_points_for_navigator_script},
            )
        chrome.execute_cdp_cmd(
            scripts.add_script_to_evaluate_on_new_document,
            {"source": scripts.remove_extra_objects_from_window_script},
        )
        original(*args, **kwargs)

    chrome.get = override


def __add_virtual_authenticator(chrome: WebDriver):
    try:
        # For Python 3.7+
        from selenium.webdriver.common.virtual_authenticator import (
            Transport,
            VirtualAuthenticatorOptions,
        )

        auth_options = VirtualAuthenticatorOptions()
        auth_options.transport = Transport.INTERNAL
        auth_options.has_user_verification = True
        auth_options.is_user_verified = True
        auth_options.is_user_consenting = True
        chrome.add_virtual_authenticator(auth_options)
    except Exception as e:
        logger.debug("Could not attach a virtual authenticator | %s", e)


def create_chrome(
    options: Optional["ChromeOptions"] = None,
    timeout: Optional[float] = None,
    headless: bool = True,
    log_level: int = 0,
    host: str = "127.0.0.1",
    port: Optional[int] = None,
    user_data_dir: Optional[str] = None,
) -> WebDriver:
    """
    Acquire a chrome browser instane. There is a limit of the number of
    browser instances you can keep open at a time. You must call quit()
    to cleanup existing browser.

    ```
    chrome = Chrome().browser()
    chrome.quit()
    ```

    NOTE: You must call quit() to cleanup the queue for next instances.
    """
    assert __semaphore.acquire(True, timeout), "Failed to acquire semaphore"

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

    # Suppress bothersome stuffs
    options.add_argument("--log-level=0")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-first-run")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # debug_host = "127.0.0.1"
    # debug_port = free_port(debug_host)
    # options.add_argument("--remote-debugging-host=%s" % debug_host)
    # options.add_argument("--remote-debugging-port=%s" % debug_port)

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

    executable_path = __get_driver_path()
    logger.debug(
        "Creating chrome instance | "
        + f"headless={headless} | "
        + f"driver_path={executable_path}"
    )
    try:
        chrome = WebDriver(
            executable_path=executable_path,
            options=options,
        )
    except Exception:
        chrome = None

    if not chrome:
        raise LNException("Failed to create chrome instance")

    logger.info("Created chrome instance > %s", chrome.session_id)
    chrome.set_window_position(0, 0)
    __open_browsers.append(chrome)
    __override_quit(chrome)
    __override_get(chrome)
    __add_virtual_authenticator(chrome)
    return chrome
