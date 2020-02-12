from enum import Enum, auto


class ScrapStep(Enum):
    INITIALIZE = auto()
    DO_LOGIN = auto()
    PREPARE_SEARCH_URL = auto()
    PARSE_SEARCH_RESULTS = auto()
    PREPARE_NOVEL_PAGE_URL = auto()
    PARSE_NOVEL_INFO = auto()
    PARSE_VOLUME_LIST = auto()
    GET_VOLUME_INFO = auto()
    PARSE_CHAPTER_LIST = auto()
    GET_CHAPTER_INFO = auto()
    PREPARE_CHAPTER_PAGE_URL = auto()
    PARSE_CHAPTER_CONTENT = auto()
    GET_CHAPTER_IMAGES = auto()
    GET_CHAPTER_PARAGRAPHS = auto()
    FINALIZE = auto()
