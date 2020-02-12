# -*- coding: utf-8 -*-
from enum import Enum, auto


class RequestType(Enum):
    INITIALIZE = auto()
    CREATE_AUTHOR_INSTANCE = auto()
    CREATE_NOVEL_INSTANCE = auto()
    CREATE_VOLUME_INSTANCE = auto()
    CREATE_CHAPTER_INSTANCE = auto()
    PARSE_NOVEL_URL = auto()
    PARSE_NOVEL_NAME = auto()
    PARSE_NOVEL_COVER = auto()
    PARSE_NOVEL_AUTHORS = auto()
    PARSE_NOVEL_DETAILS = auto()
    PARSE_NOVEL_CHAPTER_LIST = auto()
    PARSE_CHAPTER_BODY = auto()
    FINALIZE = auto()
