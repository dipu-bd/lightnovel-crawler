#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Original source: https://github.com/anqxyr/racovimge
"""

###############################################################################
# Module Imports
###############################################################################

import base64
import logging
import os.path
import pathlib
import random as rand
import shutil
import subprocess
import tempfile
import textwrap

import jinja2


logger = logging.getLogger(__name__)


###############################################################################
# Templates and Color Schemes
###############################################################################

asset_path = os.path.join(__file__, '..', '..', 'assets')
ROOT = pathlib.Path(os.path.normpath(asset_path))

templates = [i.stem for i in (ROOT / 'templates').glob('*.svg')]

with (ROOT / 'colors.txt').open() as file:
    color_schemes = [i.split() for i in file.read().split('\n')]

fonts = ROOT / 'fonts'
fonts = [i for i in fonts.glob('*.*') if i.suffix in ('.ttf', '.otf')]
fonts = [str(i.resolve()) for i in fonts]


###############################################################################
# Jinja2 setup
###############################################################################

def to_rgb(color):
    color = color.lstrip('#')
    r, g, b = map(lambda x: int(x, 16), [color[:2], color[2:4], color[4:]])
    return 'rgb({},{},{})'.format(r, g, b)


def wrap(text, width):
    if not isinstance(text, str):
        return text
    return textwrap.wrap(
        text, break_long_words=False, break_on_hyphens=False, width=width)


template_dir = os.path.abspath(str(ROOT / 'templates'))
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(searchpath=template_dir))
env.filters['wrap'] = wrap
env.filters['rgb'] = to_rgb


###############################################################################
# Covers
###############################################################################

def random_cover(title, author):
    font_size_title = 120
    font_size_author = 52
    font = rand.choice(fonts)
    template = rand.choice(templates)
    colors = rand.choice(color_schemes)
    color1, color2, color3, color4, color5 = colors

    author = author.split('; ') if isinstance(author, str) else author
    authors = [author] if isinstance(author, str) else author
    authors = authors[:3] if authors else []

    font_mimetypes = dict(
        otf='font/opentype',
        ttf='application/x-font-ttf'
    )

    font = pathlib.Path(font)
    with font.open('rb') as file:
        font_data = file.read()
        font_data = base64.b64encode(font_data).decode('utf-8')
    # end with
    font_name = font.stem
    font_type = font_mimetypes[font.suffix.lstrip('.')]

    kargs = dict(
        title=title,
        authors=authors,
        font=font_name,
        font_type=font_type,
        font_data=font_data,
        color1=color1,
        color2=color2,
        color3=color3,
        color4=color4,
        color5=color5,
        font_size=font_size_title,
        font_size_author=font_size_author,
    )
    logger.debug(
        'Cover image: template = %s, font = %s [%s]',
        template, font_name, font_type
    )

    return env.get_template(template + '.svg').render(**kargs)
# end def
