from contextlib import suppress
import logging
import subprocess
import sys
from threading import Thread
import time
from typing import Optional
from urllib.request import urlopen

from ..context import ctx
from ..enums import UserRole
from ..utils.browser_detect import pick_executable
from ..utils.platforms import Screen
from ..utils.sockets import free_port

logger = logging.getLogger(__name__)

APP_NAME = "Lightnovel Crawler"

# How long we allow the server to finish first-run work (migrations, seeding,
# source loading) before giving up and showing the error to the user.
READY_TIMEOUT = 120.0

# If the browser process dies within this window after launch, the window never
# actually opened — fall back to the system browser instead.
LAUNCH_GRACE = 3.0

_SPINNER = "|/-\\"


class FallbackException(Exception):
    """Raised when the app-mode window can't be used and we should fall back
    to opening the URL in the user's default browser."""


# ---------------------------------------------------------------------------
# Console output helpers
# ---------------------------------------------------------------------------


def _line(message: str = "") -> None:
    print(message, flush=True)


def _status(message: str) -> None:
    print(f"  {message}", flush=True)


def _banner() -> None:
    bar = "=" * 52
    _line()
    _line(bar)
    _line(f"  {APP_NAME}")
    _line(bar)
    _line()


# ---------------------------------------------------------------------------
# Windows console show/hide
# ---------------------------------------------------------------------------

_console_hidden = False


def _console_hwnd():
    if sys.platform != "win32":
        return None
    import ctypes

    with suppress(Exception):
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        return hwnd or None
    return None


def _owns_console() -> bool:
    """True when this process is the sole owner of its console window.

    An auto-created console (a frozen double-click launch) has exactly one
    attached process — us — so hiding it is safe. A console inherited from the
    user's terminal has more attached processes and must never be hidden."""
    if sys.platform != "win32":
        return False
    import ctypes

    with suppress(Exception):
        buffer = (ctypes.c_uint * 4)()
        count = ctypes.windll.kernel32.GetConsoleProcessList(buffer, 4)
        return count == 1
    return False


def _hide_console() -> None:
    global _console_hidden
    hwnd = _console_hwnd()
    if not hwnd:
        return
    import ctypes

    ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE  # type: ignore[attr-defined]
    _console_hidden = True


def _restore_console() -> None:
    """Bring a previously hidden console back so the user can read errors."""
    global _console_hidden
    if not _console_hidden:
        return
    hwnd = _console_hwnd()
    if hwnd:
        import ctypes

        ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW  # type: ignore[attr-defined]
        ctypes.windll.user32.SetForegroundWindow(hwnd)  # type: ignore[attr-defined]
    _console_hidden = False


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------


def _start_server(host: str, port: int) -> None:
    from ..commands.server import server

    ctx.setup(
        log_level=0,
        reset_db_on_failure=True,
    )
    server(host=host, port=port)


def _wait_for_ready(
    host: str,
    port: int,
    server_error: dict,
    server_thread: Thread,
) -> None:
    """Block until the server answers /health, or raise with a clear reason.

    A /health 200 is only served after the lifespan's ctx.setup() completes, so
    it doubles as the readiness signal and removes the token-generation race."""
    url = f"http://{host}:{port}/health"
    deadline = time.monotonic() + READY_TIMEOUT
    last_error: Optional[BaseException] = None
    frame = 0

    print("  Starting the server  ", end="", flush=True)
    while time.monotonic() < deadline:
        # Surface a crashed server thread immediately instead of timing out.
        error = server_error.get("error")
        if error is not None:
            _line()
            raise error

        try:
            with urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    print("\r  Server is ready.            ", flush=True)
                    return
        except Exception as e:
            last_error = e

        # uvicorn swallows a lifespan-startup failure and returns without raising, so the
        # thread ends with no error set. Fail fast instead of polling a dead port for the
        # full timeout.
        if not server_thread.is_alive():
            _line()
            raise RuntimeError(
                "The server stopped before becoming ready; check the log above for the cause."
            ) from last_error

        print(f"\r  Starting the server {_SPINNER[frame % len(_SPINNER)]} ", end="", flush=True)
        frame += 1
        time.sleep(0.2)

    _line()
    raise TimeoutError(
        f"The server did not become ready within {int(READY_TIMEOUT)} seconds."
    ) from last_error


def _build_url(host: str, port: int) -> str:
    token = ctx.users.generate_token(
        user=ctx.users.get_admin(),
        expiry_minutes=1 * 365 * 24 * 60,  # 1 year
        scopes=[UserRole.LOCAL],
    )
    return f"http://{host}:{port}/?authToken={token}"


# ---------------------------------------------------------------------------
# Window launchers
# ---------------------------------------------------------------------------


def _launch_app_window(url: str, manage_console: bool) -> None:
    binary = pick_executable()
    if not binary:
        raise FallbackException("No Chromium-based browser found")

    storage_path = ctx.config.app.app_dir / "app-browser"
    width = min(1400, Screen.view_width - 20)
    height = min(1000, Screen.view_height - 80)
    args = [
        str(binary),
        f"--app={url}",
        "--new-window",
        f"--window-size={width},{height}",
        f"--user-data-dir={storage_path}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    logger.info(f"Opening app-mode browser: {binary}")
    proc = subprocess.Popen(args)
    logger.info(f"Started app (pid={proc.pid})")

    # If the browser exits during the grace window, the window never opened.
    grace_deadline = time.monotonic() + LAUNCH_GRACE
    while time.monotonic() < grace_deadline:
        code = proc.poll()
        if code is not None:
            raise FallbackException(f"Browser exited early (code={code})")
        time.sleep(0.1)

    _line()
    _status("The application is now open in a separate window.")
    if manage_console and _owns_console():
        _status("This console will hide. Closing the app window stops the server.")
        _hide_console()
    else:
        _status("Keep this window open. Closing it stops the server.")

    try:
        proc.wait()
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(2)
            except BaseException:
                proc.kill()
        logger.info(f"Closed app (pid={proc.pid}): {proc.poll()}")


def _run_in_system_browser(url: str) -> None:
    _restore_console()
    _line()
    _status("Opening in your default web browser:")
    _line()
    _line(f"    {url}")
    _line()

    with suppress(Exception):
        import webbrowser

        webbrowser.open(url)

    _status("The server is running. Keep this window open to keep it running.")
    with suppress(EOFError, KeyboardInterrupt):
        input("  Press Enter to stop the server... ")


def _fatal(message: str, error: BaseException) -> None:
    _restore_console()
    logger.error(message, exc_info=error)
    _line()
    _line("  " + "-" * 48)
    _status(f"[ERROR] {message}")
    _status(f"Reason: {error}")
    _line("  " + "-" * 48)
    _line()
    _status("The application could not start. Review the messages above.")
    with suppress(EOFError, KeyboardInterrupt):
        input("  Press Enter to close... ")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def start(manage_console: bool = False) -> None:
    """Launch the desktop app.

    The console stays visible during startup so any failure is readable; on a
    successful launch it is hidden (only when we own it — see _owns_console).
    Pass manage_console=True from the frozen double-click path; leave it False
    when invoked from a real terminal (`lncrawl app`) so the user's shell is
    never hidden."""
    _banner()

    host = "localhost"
    port = free_port(host, 31580)

    server_error: dict = {}

    def _run_server() -> None:
        try:
            _start_server(host, port)
        except BaseException as e:
            server_error["error"] = e
            logger.exception("Server thread crashed")

    server_thread = Thread(daemon=True, name="server", target=_run_server)
    server_thread.start()

    try:
        _wait_for_ready(host, port, server_error, server_thread)
        url = _build_url(host, port)
    except Exception as e:
        _fatal("The server failed to start.", e)
        return

    _status("Opening the application window...")
    try:
        _launch_app_window(url, manage_console)
    except FallbackException as e:
        logger.info(f"App-mode window unavailable: {e}")
        _run_in_system_browser(url)
    except Exception:
        logger.exception("App window error")
        _restore_console()
        _status("Could not open the app window; using your default browser instead.")
        _run_in_system_browser(url)
