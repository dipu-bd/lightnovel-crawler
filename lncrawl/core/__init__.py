"""
Interactive application to take user inputs
"""

import logging
import os
import sys

import colorama  # type:ignore

logger = logging.getLogger(__name__)


def init():
    from ..assets.version import get_version
    from .arguments import get_args
    from .display import description, input_suppression
    from .logconfig import configure_logging

    os.environ["version"] = get_version()

    colorama.init(wrap=True)
    description()

    configure_logging()

    args = get_args()
    logger.debug("Arguments: %s", args)

    if args.suppress:
        input_suppression()
        print(args)

    if args.bot:
        os.environ["BOT"] = args.bot

    for key, val in args.extra.items():
        os.environ[key] = val[0]


def start_app():
    from ..bots import run_bot
    from .arguments import get_args
    from .display import cancel_method, error_message
    from .proxy import load_proxies, start_proxy_fetcher, stop_proxy_fetcher
    from .sources import load_sources

    init()

    load_sources()
    cancel_method()

    args = get_args()
    if args.proxy_file:
        os.environ["use_proxy"] = "file"
        load_proxies(args.proxy_file)

    if args.auto_proxy:
        os.environ["use_proxy"] = "auto"
        start_proxy_fetcher()

    try:
        bot = os.getenv("BOT", "").lower()
        run_bot(bot)
    except KeyboardInterrupt:
        pass
    except Exception:
        error_message(*sys.exc_info())

    if args.auto_proxy:
        stop_proxy_fetcher()

    if (
        getattr(sys, "frozen", False)
        and hasattr(sys, "_MEIPASS")
        and not args.close_directly
    ):
        try:
            input("Press ENTER to exit...")
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
