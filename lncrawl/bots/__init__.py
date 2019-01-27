#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def run_bot(bot):
    if bot == 'telegram':
        from ..bots.telegram import TelegramBot
        TelegramBot().start()
    elif bot == 'discord':
        from ..bots.discord import DiscordBot
        DiscordBot().start_bot()
    else:
        from ..bots.console import ConsoleBot
        ConsoleBot().start()
    # end def
# end def
