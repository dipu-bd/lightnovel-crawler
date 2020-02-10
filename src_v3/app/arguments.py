# -*- coding: utf-8 -*-
from ..assets import get_version
from .utility.argument import Namespace, ArgumentBuilder as Arg

_builder = Arg(group=[
    Arg('-v', '--version', action='version',
        version='Lightnovel Crawler ' + get_version()),
    Arg('--config', dest='config', metavar='CONFIG_FILE',
        help='The config file path'),
])


def get_args() -> Namespace:
    return _builder.parse()
