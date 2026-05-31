import questionary

from ...context import ctx


def prompt_section() -> str:
    return questionary.select(
        "Select a section:",
        choices=sorted([k for k in ctx.config._data.keys() if k != "__deprecated__"]),
    ).unsafe_ask()


def prompt_key(section: str) -> str:
    return questionary.select(
        "Select a key:",
        choices=sorted(ctx.config._data[section].keys()),
    ).unsafe_ask()


def prompt_value(section: str, key: str) -> str:
    value = ctx.config.get(section, key)
    return questionary.text(
        "Enter value:",
        default=str(value),
    ).unsafe_ask()
