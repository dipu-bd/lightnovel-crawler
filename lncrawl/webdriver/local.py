import logging
import os
from typing import List, Optional

import nodriver

from ..exceptions import LNException
from ..utils.async_loop import run_async
from ..utils.browser_detect import pick_executable
from ..utils.platforms import Platform, Screen
from .job_queue import acquire_queue, release_queue

logger = logging.getLogger(__name__)


def create_local(
    extra_args: Optional[List[str]] = None,
    timeout: Optional[float] = None,
    headless: bool = False,
    user_data_dir: Optional[str] = None,
    **kwargs,
) -> nodriver.Browser:
    """
    Acquire a nodriver browser instance. Blocks until a slot is available in the
    semaphore pool. Call browser.stop() to release the slot.
    """
    acquire_queue(timeout)

    executable = pick_executable()
    if not executable:
        raise LNException(
            "No Chromium-based browser found. "
            "Please install Chrome, Edge, Brave, Vivaldi, Yandex, or Whale."
        )

    if not headless and not Platform.has_display:
        headless = True

    browser_args = []
    if headless:
        browser_args += [
            "--window-size=1920,1080",
        ]
    else:
        width = max(640, Screen.view_width * 3 // 4)
        height = max(480, Screen.view_height * 3 // 4)
        width = int(os.getenv("CHROME_WIDTH", width))
        height = int(os.getenv("CHROME_HEIGHT", height))
        browser_args.append(f"--window-size={width},{height}")

    if extra_args:
        browser_args += extra_args

    is_debug = bool(os.getenv("debug_mode"))
    if not is_debug:
        browser_args += ["--log-level=3", "--disable-logging"]

    # Disable sandbox when headless on Linux/Docker/CI — Chrome requires this
    # when running as root or in restricted container environments.
    sandbox = not (headless and (Platform.linux or Platform.docker or Platform.ci))

    browser = run_async(
        nodriver.start(
            headless=headless,
            sandbox=sandbox,
            browser_executable_path=executable,
            browser_args=browser_args,
            user_data_dir=user_data_dir,
        ),
        timeout=timeout,
    )

    logger.info("Created nodriver browser instance")
    release_queue(browser)
    return browser
