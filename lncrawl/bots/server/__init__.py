import logging
import os

import uvicorn

from lncrawl.core.arguments import get_args

from .app import app
from .context import ServerContext


class ServerBot:
    log = logging.getLogger(__name__)

    def start(self):
        args = get_args()
        os.putenv("debug_mode", 'true')

        ctx = ServerContext()
        ctx.db.prepare()
        ctx.users.prepare()
        ctx.scheduler.start()

        uvicorn.run(
            app,
            log_level=logging.DEBUG,
            port=args.server_port or 8080,
            host=args.server_host or '0.0.0.0',
        )
