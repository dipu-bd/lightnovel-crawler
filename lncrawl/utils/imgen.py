# https://github.com/alexwlchan/specktre

import random
from typing import List, Optional

from PIL import Image, ImageDraw

from .material_colors import ColorName, ColorWeight, generate_colors
from .tilings import TileGenerator, generate_tiles


def generate_image(
    filename: Optional[str] = None,
    width: int = 512,
    height: int = 512,
    color_names: List[ColorName] = [],
    color_weights: List[ColorWeight] = [],
    generator: Optional[TileGenerator] = None,
    side_length: int = 50,
) -> Image:
    tiles = generate_tiles(
        generator,
        width,
        height,
        side_length,
    )
    colors = generate_colors(
        color_names,
        color_weights,
    )
    im = Image.new(
        mode="RGB",
        size=(width, height),
    )
    for tile, color in zip(tiles, colors):
        ImageDraw.Draw(im).polygon(tile, fill=color)

    if filename:
        im.save(filename)

    return im


good_color_names = set(ColorName).difference(
    [
        ColorName.black,
        ColorName.white,
        ColorName.light_blue,
        ColorName.light_green,
    ]
)
good_color_weights = set(ColorWeight).difference(
    [
        ColorWeight.main,
        ColorWeight.w50,
        ColorWeight.w100,
        ColorWeight.w200,
        ColorWeight.w800,
        ColorWeight.w900,
        ColorWeight.a100,
        ColorWeight.a200,
    ]
)


def generate_cover_image(
    filename: Optional[str] = None,
    width: int = 800,
    height: int = 1032,
) -> Image:
    generate_image(
        filename=filename,
        width=width,
        height=height,
        color_names=good_color_names,
        color_weights=good_color_weights,
        side_length=random.randint(300, 750),
    )
