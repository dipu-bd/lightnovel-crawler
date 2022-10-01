import random
from enum import Enum
from typing import Generator, List, Tuple

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
    names: List[ColorName] = [],
    weights: List[ColorWeight] = [],
) -> Tuple[int, int, int]:
    if not names:
        names = list(ColorName)
    if not weights:
        weights = list(ColorWeight)

    available_names = set(material_colors.keys())
    names = list(available_names.intersection(names))
    if not names:
        names = list(available_names)
    name = random.choice(names)

    available_weights = set(material_colors[name].keys())
    weights = list(available_weights.intersection(weights))
    if not weights:
        return material_colors[name][""]
    weight = random.choice(weights)

    return tuple(material_colors[name][weight])


def generate_colors(
    names: List[ColorName] = [],
    weights: List[ColorWeight] = [],
) -> Generator[Tuple[int, int, int], None, None]:
    if not names:
        names = list(ColorName)
    if not weights:
        weights = list(ColorWeight)

    available_names = set(material_colors.keys())
    names = list(available_names.intersection(names))
    if not names:
        names = list(available_names)

    weights_map = {}
    for name in names:
        available_weights = set(material_colors[name].keys())
        weights = list(available_weights.intersection(weights))
        if not weights:
            weights = list(available_weights)
        weights_map[name] = weights

    while True:
        name = random.choice(names)
        if weights_map[name]:
            weight = random.choice(list(weights_map[name]))
        else:
            weight = ""
        yield tuple(material_colors[name][weight])
