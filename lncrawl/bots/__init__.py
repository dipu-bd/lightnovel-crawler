# -*- coding: utf-8 -*-

supported_bots = [
    'console',
    'telegram',
    'discord',
]


def run_bot(bot):
    if bot not in supported_bots:
        bot = 'console'
    # end if
    if bot == 'console':
        from ..bots.console import ConsoleBot
        ConsoleBot().start()
    elif bot == 'telegram':
        from ..bots.telegram import TelegramBot
        TelegramBot().start()
    elif bot == 'discord':
        from ..bots.discord import DiscordBot
        DiscordBot().start_bot()
    else:
        print('Unknown bot: %s' % bot)
    # end def
# end def
