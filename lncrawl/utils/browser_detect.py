import logging
import os
from typing import Iterable, List

from .platforms import Platform

logger = logging.getLogger(__name__)


def find_executables(
    windows_path: Iterable[str],
    mac_app_path: Iterable[str],
    linux_app_path: Iterable[str],
    posix_app_name: Iterable[str],
    windows_exe_name: Iterable[str],
) -> List[str]:
    candidates = []
    if Platform.posix:
        for item in os.environ["PATH"].split(os.pathsep):
            for subitem in posix_app_name:
                candidates.append(os.path.join(item, subitem))
        if Platform.linux:
            candidates += list(linux_app_path)
        if Platform.mac:
            candidates += list(mac_app_path)

    if Platform.windows:
        for path in (
            "PROGRAMFILES",
            "PROGRAMFILES(X86)",
            "LOCALAPPDATA",
            "PROGRAMW6432",
        ):
            if path in os.environ:
                item = os.environ[path]
                for inner_path in windows_path:
                    subitem = os.sep.join(inner_path.split("/"))
                    for exe_name in windows_exe_name:
                        candidates.append(os.path.join(item, subitem, exe_name))

    valids: List[str] = []
    for candidate in candidates:
        item = os.path.normpath(candidate)
        if os.path.exists(item) and os.access(item, os.X_OK):
            logger.debug(f"{item} is a valid!")
            valids.append(item)

    return valids


def find_chrome_executables() -> List[str]:
    """
    Scans standard cross-platform operating system installations
    to auto-detect the chrome, beta, canary, chromium executable path.
    """
    return find_executables(
        posix_app_name=(
            "google-chrome",
            "chromium",
            "chromium-browser",
            "chrome",
            "google-chrome-stable",
            "com.google.Chrome",
        ),
        linux_app_path=[
            "/var/lib/flatpak/exports/bin/com.google.Chrome",
        ],
        mac_app_path=[
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ],
        windows_path=[
            "Google/Chrome/Application",
            "Google/Chrome Beta/Application",
            "Google/Chrome Canary/Application",
        ],
        windows_exe_name=[
            "chrome.exe",
        ],
    )


def find_edge_executables() -> List[str]:
    """
    Scans standard cross-platform operating system installations
    to auto-detect the Microsoft Edge executable path.
    """
    return find_executables(
        posix_app_name=(
            "microsoft-edge",
            "microsoft-edge-stable",
            "microsoft-edge-beta",
        ),
        linux_app_path=[],
        mac_app_path=[
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ],
        windows_path=[
            "Microsoft/Edge/Application",
        ],
        windows_exe_name=[
            "msedge.exe",
        ],
    )


def pick_executable(available: List[str]) -> str:
    """
    Returns the executable with the shorted path
    """
    if not available:
        raise FileNotFoundError("No valid executable file path found.")

    if len(available) == 1:
        return available[0]

    return min(available, key=len)
