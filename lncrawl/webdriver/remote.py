import json
import locale
import logging
import os
from typing import Optional

from selenium.webdriver import ChromeOptions
from selenium.webdriver import Remote as WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER

from ..core.exeptions import LNException
from ..core.soup import SoupMaker
from .elements import WebElement, _add_virtual_authenticator
from .job_queue import _acquire_queue, _release_queue
from .scripts import _override_get

logger = logging.getLogger(__name__)


def create_remote(
    address: str = "http://localhost:4444",
    options: Optional["ChromeOptions"] = None,
    timeout: Optional[float] = None,
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

    # Configure window behavior
    options.add_argument("--start-maximized")

    # Logging configs
    LOGGER.setLevel(logging.WARN)
    options.add_argument(f"--log-level={0 if is_debug else 3}")
    if not is_debug:
        LOGGER.setLevel(1000)

    # Suppress bothersome stuffs
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-first-run")

    # Add capabilities
    #options.set_capability("quietExceptions", True)
    options.set_capability("acceptInsecureCerts", True)
    #options.set_capability("useAutomationExtension", False)

    # Chrome specific experimental options
    options.accept_insecure_certs = True
    options.unhandled_prompt_behavior = "dismiss"
    options.strict_file_interactability = False
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if not is_debug:
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Set default language
    try:
        language = locale.getdefaultlocale()[0].replace("_", "-")
    except Exception:
        pass
    options.add_argument("--lang=%s" % (language or "en-US"))

    # Configure user data dir
    user_data_dir = "/home/seluser"
    if user_data_dir and os.access(user_data_dir, mode=os.F_OK):
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
        logger.debug("Creating remote instance | " + f"address={address}")
        chrome = WebDriver(
            command_executor=address,
            options=options,
            desired_capabilities=options.to_capabilities(),
        )
    except Exception as e:
        logger.exception("Failed to create remote instance", e)
        chrome = None

    if not chrome:
        raise LNException("Could not obtain a webdriver")

    logger.info("Created remote instance > %s", chrome.session_id)

    if not soup_maker:
        soup_maker = SoupMaker()
    chrome._soup_maker = soup_maker
    chrome._web_element_cls = WebElement

    _add_virtual_authenticator(chrome)
    _override_get(chrome)
    _release_queue(chrome)

    return chrome
