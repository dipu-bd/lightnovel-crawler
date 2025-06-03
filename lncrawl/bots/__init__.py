supported_bots = [
    "console",
    "telegram",
    "discord",
    "lookup",
    "server",
]


def run_bot(bot):
    if bot not in supported_bots:
        bot = "console"

    if bot == "console":
        from ..bots.console import ConsoleBot
        ConsoleBot().start()

    elif bot == "telegram":
        from ..bots.telegram import TelegramBot
        TelegramBot().start()

    elif bot == "discord":
        from ..bots.discord import DiscordBot
        DiscordBot().start_bot()

    elif bot == "lookup":
        from ..bots.lookup import LookupBot
        LookupBot().start()

    if bot == "server":
        from ..bots.server import ServerBot
        ServerBot().start()

    else:
        print("Unknown bot: %s" % bot)
