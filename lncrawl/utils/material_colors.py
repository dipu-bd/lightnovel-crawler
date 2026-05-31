from enum import Enum
import random
from typing import Generator, Tuple

from ..assets.colors import material_colors


class ColorName(str, Enum):
    red = "red"
    pink = "pink"
    purple = "purple"
    deep_purple = "deep-purple"
    indigo = "indigo"
    blue = "blue"
    light_blue = "light-blue"
    cyan = "cyan"
    teal = "teal"
    green = "green"
    light_green = "light-green"
    lime = "lime"
    yellow = "yellow"
    amber = "amber"
    orange = "orange"
    deep_orange = "deep-orange"
    brown = "brown"
    grey = "grey"
    blue_grey = "blue-grey"
    white = "white"
    black = "black"

    def __str__(self):
        return self.value


class ColorWeight(str, Enum):
    main = ""
    w50 = "50"
    w100 = "100"
    w200 = "200"
    w300 = "300"
    w400 = "400"
    w500 = "500"
    w600 = "600"
    w700 = "700"
    w800 = "800"
    w900 = "900"
    a100 = "a100"
    a200 = "a200"
    a400 = "a400"
    a700 = "a700"

    def __str__(self):
        return self.value


def random_color(
    names=set(ColorName),
    weights=set(ColorWeight),
) -> Tuple[int, int, int]:
    available_names = set(material_colors.keys())
    selected_names = available_names.intersection(names)
    name = random.choice(list(selected_names or available_names))

    available_weights = set(material_colors[name].keys())
    selected_weights = available_names.intersection(weights)
    weight = random.choice(list(selected_weights or available_weights))

    r, g, b = material_colors[name][weight]
    return (r, g, b)


def generate_colors(
    names=set(ColorName),
    weights=set(ColorWeight),
) -> Generator[Tuple[int, int, int], None, None]:
    while True:
        yield random_color(names, weights)
