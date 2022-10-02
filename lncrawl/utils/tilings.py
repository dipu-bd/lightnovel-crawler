"""
Generate coordinates for tilings of the plane.

Diagrams and background to this code are on my blog:
http://alexwlchan.net/2016/10/tiling-the-plane-with-pillow/
"""

import math
import random
from enum import Enum
from typing import Generator, List, Tuple


def generate_unit_squares(image_width, image_height):
    """Generate coordinates for a tiling of unit squares."""
    # Iterate over the required rows and cells.  The for loops (x, y)
    # give the coordinates of the top left-hand corner of each square:
    #
    #      (x, y) +-----+ (x + 1, y)
    #             |     |
    #             |     |
    #             |     |
    #  (x, y + 1) +-----+ (x + 1, y + 1)
    #
    for x in range(image_width):
        for y in range(image_height):
            yield [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]


def generate_unit_triangles(image_width, image_height):
    """Generate coordinates for a tiling of unit triangles."""
    # Our triangles lie with one side parallel to the x-axis.  Let s be
    # the length of one side, and h the height of the triangle.
    #
    # The for loops (x, y) gives the coordinates of the top left-hand corner
    # of a pair of triangles:
    #
    #           (x, y) +-----+ (x + 1, y)
    #                   \   / \
    #                    \ /   \
    #    (x + 1/2, y + h) +-----+ (x + 3/2, y + h)
    #
    # where h = sin(60°) is the height of an equilateral triangle with
    # side length 1.
    #
    # On odd-numbered rows, we translate by (s/2, 0) to make the triangles
    # line up with the even-numbered rows.
    #
    # To avoid blank spaces on the edge of the canvas, the first pair of
    # triangles on each row starts at (-1, 0) -- one width before the edge
    # of the canvas.
    h = math.sin(math.pi / 3)

    for x in range(-1, image_width):
        for y in range(int(image_height / h)):

            # Add a horizontal offset on odd numbered rows
            x_ = x if (y % 2 == 0) else x + 0.5

            yield [(x_, y * h), (x_ + 1, y * h), (x_ + 0.5, (y + 1) * h)]
            yield [(x_ + 1, y * h), (x_ + 1.5, (y + 1) * h), (x_ + 0.5, (y + 1) * h)]


def generate_unit_hexagons(image_width, image_height):
    """Generate coordinates for a regular tiling of unit hexagons."""
    # Let s be the length of one side of the hexagon, and h the height
    # of the entire hexagon if one side lies parallel to the x-axis.
    #
    # The for loops (x, y) give the coordinate of one coordinate of the
    # hexagon, and the remaining coordinates fall out as follows:
    #
    #                     (x, y) +-----+ (x + 1, y)
    #                           /       \
    #                          /         \
    #         (x - 1/2 y + h) +           + (x + 3/2, y + h)
    #                          \         /
    #                           \       /
    #                 (x, y + 2h) +-----+ (x + 1, y + 2h)
    #
    # In each row we generate hexagons in the following pattern
    #
    #         /‾‾‾\   /‾‾‾\   /‾‾‾\
    #         \___/   \___/   \___/
    #
    # and the next row is offset to fill in the gaps. So after two rows,
    # we'd have the following pattern:
    #
    #         /‾‾‾\   /‾‾‾\   /‾‾‾\
    #         \___/‾‾‾\___/‾‾‾\___/‾‾‾\
    #             \___/   \___/   \___/
    #
    # There are offsets to ensure we fill the entire canvas.

    # Half the height of the hexagon
    h = math.sin(math.pi / 3)

    for x in range(-1, image_width, 3):
        for y in range(-1, int(image_height / h) + 1):

            # Add the horizontal offset on every other row
            x_ = x if (y % 2 == 0) else x + 1.5

            yield [
                (x_, y * h),
                (x_ + 1, y * h),
                (x_ + 1.5, (y + 1) * h),
                (x_ + 1, (y + 2) * h),
                (x_, (y + 2) * h),
                (x_ - 0.5, (y + 1) * h),
            ]


###################################################################################
#                               EXTRA UTILITIES                                   #
# https://github.com/dipu-bd/lightnovel-crawler/blob/dev/lncrawl/utils/tilings.py #
###################################################################################


class TileGenerator(Enum):
    squares = generate_unit_squares
    hexagons = generate_unit_hexagons
    triangles = generate_unit_triangles

    def __str__(self):
        return self.name

    def __call__(
        self,
        image_width: int,
        image_height: int,
    ) -> Generator[List[Tuple[int, int]], None, None]:
        self.value(image_width, image_height)


def random_generator() -> TileGenerator:
    return random.choice(
        [
            TileGenerator.squares,
            TileGenerator.hexagons,
            TileGenerator.triangles,
        ]
    )


def generate_tiles(
    generator: TileGenerator,
    image_width: int,
    image_height: int,
    side_length: int = 50,
) -> Generator[List[Tuple[int, int]], None, None]:
    if not isinstance(generator, TileGenerator):
        generator = random_generator()

    scaled_width = math.ceil(image_width / side_length) + 1
    scaled_height = math.ceil(image_height / side_length) + 1

    for tiles in generator(scaled_width, scaled_height):
        yield [(x * side_length, y * side_length) for (x, y) in tiles]
