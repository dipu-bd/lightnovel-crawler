from contextlib import suppress
import json
import logging
from pathlib import Path
import socket
import subprocess
from threading import Thread
import time
from urllib.request import urlopen

from websockets.sync.client import connect as ws_connect

from ..assets.htmls import loading_path
from ..assets.images import lncrawl_icon
from ..context import ctx
from ..enums import UserRole
from ..utils.browser_detect import pick_executable
from ..utils.platforms import Screen
from ..utils.sockets import free_port

logger = logging.getLogger(__name__)


class FallbackException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def _start_server(host: str, port: int):
    from ..commands.server import server

    ctx.setup(
        log_level="INFO",
        reset_db_on_failure=True,
    )
    server(host=host, port=port)


def _wait_to_connect(host: str, port: int, timeout: float = 60) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.1):
                return True
        except OSError:
            pass
    raise Exception("Failed to connect with server")


def _build_url(host: str, port: int) -> str:
    _wait_to_connect(host, port)
    token = ctx.users.generate_token(
        user=ctx.users.get_admin(),
        expiry_minutes=100 * 365 * 24 * 60,  # 100 years
        scopes=[UserRole.LOCAL],
    )
    return f"http://{host}:{port}/?authToken={token}"


def _start_app_in_browser(
    host: str,
    port: int,
    cdp_port: int,
    storage_path: Path,
):
    # get chrome-like browser binary
    binary = pick_executable()
    if not binary:
        raise FallbackException("No chrome-like binary found")

    # start process
    logger.info(f"Opening app-mode browser: {binary}")
    width = min(1400, Screen.view_width - 20)
    height = min(1000, Screen.view_height - 80)
    args = [
        str(binary),
        f"--app={loading_path().as_uri()}",
        "--new-window",
        f"--window-size={width},{height}",
        f"--user-data-dir={storage_path}",
        f"--remote-debugging-port={cdp_port}",
    ]
    proc = subprocess.Popen(args)
    logger.info(f"Started app (pid=${proc.pid})")

    try:
        #  wait for CDP to be ready
        if not _wait_to_connect(host, cdp_port):
            raise Exception("Failed to connect with CDP")

        # get CDP url
        with urlopen(f"http://{host}:{cdp_port}/json") as resp:
            targets = json.loads(resp.read())
            ws_url = targets[0]["webSocketDebuggerUrl"]
            logger.info(f"CDP URL={ws_url}")

        # wait for the server
        url = _build_url(host, port)
        logger.info(f"Launching URL: {url}")

        # send URL via CDP
        with ws_connect(ws_url) as ws:
            ws.send(
                json.dumps(
                    {
                        "id": 1,
                        "method": "Page.navigate",
                        "params": {"url": url},
                    }
                )
            )

        # wait for exit
        proc.wait()
    finally:
        # terminate forcefully
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(2)
            except BaseException:
                proc.kill()
        logger.info(f"Closed app (pid=${proc.pid}): {proc.poll()}")


def _start_fallback_window(host: str, port: int) -> None:
    import tkinter as tk
    import webbrowser

    root = tk.Tk()
    root.title("Lightnovel Crawler")
    root.resizable(False, False)
    root.configure(bg="#141414")
    with suppress(Exception):
        root.iconbitmap(str(lncrawl_icon()))

    tk.Label(
        root,
        text="Lightnovel Crawler",
        bg="#141414",
        fg="#e8e8e8",
        font=("Segoe UI", 13, "bold"),
    ).pack(anchor="w", padx=20, pady=(16, 4))

    status_lbl = tk.Label(
        root,
        text="Starting server…",
        bg="#141414",
        fg="#8b949e",
        font=("Segoe UI", 9),
        justify="left",
    )
    status_lbl.pack(anchor="w", padx=20)

    url_frame = tk.Frame(root, bg="#1e1e1e")
    url_frame.pack(fill="x", padx=20, pady=12)
    url_lbl = tk.Label(
        url_frame,
        text=f"http://{host}:{port}",
        bg="#1e1e1e",
        fg="#888888",
        font=("Courier New", 10),
        padx=12,
        pady=8,
    )
    url_lbl.pack(side="left")

    btn_frame = tk.Frame(root, bg="#141414")
    btn_frame.pack(padx=20, pady=(0, 16), anchor="w")
    tk.Button(
        btn_frame,
        text="Stop Server",
        command=root.destroy,
        bg="#b91c1c",
        fg="#fff",
        relief="flat",
        padx=10,
        pady=5,
        cursor="hand2",
    ).pack(side="left")

    def _on_server_ready(url: str):
        webbrowser.open(url)
        with suppress(Exception):
            status_lbl.configure(
                text="Server is running. No app-mode browser (Chrome/Edge)\n"
                "was found — opened in your default browser instead."
            )
            url_lbl.configure(
                fg="#58a6ff",
                cursor="hand2",
            )
            url_lbl.bind("<Button-1>", lambda *_: webbrowser.open(url))

    def _wait_and_open():
        url = _build_url(host, port)
        root.after(0, _on_server_ready, url)

    Thread(target=_wait_and_open, daemon=True).start()

    # wait for exit
    root.mainloop()


def start() -> None:
    host = "localhost"
    port = free_port(host, 31580)
    cdp_port = free_port(host, 31590)

    Thread(
        daemon=True,
        name="server",
        target=_start_server,
        args=(host, port),
    ).start()

    try:
        ctx.config.load()
        storage_path = ctx.config.app.app_dir / "app-browser"
        _start_app_in_browser(host, port, cdp_port, storage_path)
    except FallbackException:
        _start_fallback_window(host, port)
