import logging

import uvicorn

from ...core.arguments import get_args
from .app import app
from .context import ServerContext


class ServerBot:
    log = logging.getLogger(__name__)

    def start(self):
        args = get_args()
        ctx = ServerContext()
        ctx.runner.start()
        uvicorn.run(
            app,
            log_level=logging.DEBUG,
            port=args.server_port or 8080,
            host=args.server_host or '0.0.0.0',
        )
