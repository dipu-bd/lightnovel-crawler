import logging
import logging.config
import os

from colorama import Fore

from ...core.arguments import get_args

shard_id = get_args().shard_id
shard_count = get_args().shard_count
signal = os.getenv("DISCORD_SIGNAL_CHAR") or "!"
discord_token = os.getenv("DISCORD_TOKEN")
disable_search = os.getenv("DISCORD_DISABLE_SEARCH") == "true"
session_retain_time_in_seconds = 4 * 60 * 60
max_active_handles = 150

vip_users_ids = set(
    [
        "1822",
    ]
)

available_formats = [
    "epub",
    "text",
    "web",
    "mobi",
    #'pdf',
    #'fb2',
]

os.makedirs("logs", exist_ok=True)
logging.config.dictConfig(
    {
        #
        # Configure logging
        # Docs: https://docs.python.org/3.5/library/logging.config.html#configuration-dictionary-schema
        # Example: https://stackoverflow.com/a/7507842/1583052
        #
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "console": {
                "format": Fore.CYAN
                + "%(asctime)s"
                + Fore.RESET
                + " "
                + Fore.GREEN
                + "%(levelname)-8s"
                + Fore.RESET
                + " %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "file": {
                "format": "%(asctime)s [%(process)d] %(levelname)s\n%(name)s: %(message)s\n",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "formatter": "console",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # default is stderr
            },
            "file": {
                "formatter": "file",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"logs/discord-bot_{shard_id}.log",
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file"],
                "level": os.getenv("LOG_LEVEL", "NOTSET"),
            },
        },
    }
)

logger = logging.getLogger(f"discord-{shard_id}")

if not discord_token:
    raise Exception("Discord token is not found")
