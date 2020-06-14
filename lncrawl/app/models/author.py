# -*- coding: utf-8 -*-

from enum import IntEnum, auto


class AuthorType(IntEnum):
    UNKNOWN = auto()
    AUTHOR = auto()
    ARTIST = auto()
    TRANSLATOR = auto()
    EDITOR = auto()


class Author:
    '''Details of a author of a novel'''

    def __init__(
            self,
            name: str,
            author_type: AuthorType = AuthorType.UNKNOWN) -> None:
        super().__init__()
        self.type: AuthorType = author_type
        self.name: str = '-' if name is None else name

    def __str__(self):
        return f"<Author name:'{self.name}' type:{self.type.name}>"

    def __eq__(self, other):
        if isinstance(other, Author):
            return self.name == other.name and self.type == other.type
        else:
            return super().__eq__(other)
