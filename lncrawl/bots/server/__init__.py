import logging
import os

import uvicorn

from lncrawl.core.arguments import get_args

logger = logging.getLogger(__name__)


class ServerBot:

    def start(self):
        args = get_args()
        os.putenv("debug_mode", 'true')

        if args.server_watch:
            uvicorn.run(
                "lncrawl.bots.server.app:app",
                workers=1,
                reload=True,
                log_level=logger.level,
                port=args.server_port or 8080,
                host=args.server_host or '0.0.0.0',
            )
        else:
            from .app import app
            uvicorn.run(
                app,
                log_level=logger.level,
                port=args.server_port or 8080,
                host=args.server_host or '0.0.0.0',
            )
