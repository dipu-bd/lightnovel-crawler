from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def start_bot(token: str, guild_id: Optional[int] = None):
    from .bot import LightnovelBot

    bot = LightnovelBot(guild_id=guild_id)
    bot.run(token, log_handler=None)
