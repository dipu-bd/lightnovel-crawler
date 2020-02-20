# -*- coding: utf-8 -*-


class __Section__:
    def __init__(self, parent, name: str):
        if parent is not None:
            self.__parent__ = parent
            self.__data__ = parent.config[name]

    def save(self):
        self.__parent__.save()
