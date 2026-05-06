import logging
import socket
import threading

import webview

from ..commands.server import server
from ..config import APP_DIR
from ..context import ctx
from ..dao.enums import UserRole

logger = logging.getLogger(__name__)


def start() -> None:
    host = "localhost"

    # Find an available port
    port = 31580
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except OSError:
            s.bind((host, 0))
            port = s.getsockname()[1]

    # Setup context
    ctx.setup(reset_db_on_failure=True)
    ctx.logger.progress_bar = False
    token = ctx.users.generate_token(
        user=ctx.users.get_admin(),
        expiry_minutes=100 * 365 * 24 * 60,  # 100 years
        scopes=[UserRole.LOCAL],
    )

    # Start server in a separate thread
    t = threading.Thread(
        target=server,
        kwargs={
            "host": host,
            "port": port,
        },
        daemon=True,
        name="server",
    )
    t.start()

    # Create webview window
    webview.create_window(
        "Lightnovel Crawler",
        f"http://{host}:{port}/?authToken={token}",
        # maximized=True,
        width=1280,
        height=800,
    )

    # Persist WebView2/cookies under APP_DIR
    storage_path = str(APP_DIR / "webview")
    try:
        webview.start(
            private_mode=False,
            storage_path=storage_path,
        )
    except Exception:
        logger.exception("Webview window exited with an error")

    ctx.destroy()
