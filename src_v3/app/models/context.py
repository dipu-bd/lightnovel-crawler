# -*- coding: utf-8 -*-
from typing import List
from abc import ABC, abstractmethod, abstractproperty

from ..models import *


class AppContext(ABC):

    def __init__(self, config: Config):
        super().__init__()
        self.config: Config = config
        self.base_url: str = None
        self.novel: Novel = None
        self.volumes: List[Volume] = []
        self.chapters: List[Chapter] = []
        self.language: Language = Language.ENGLISH
        self.direction: ReadingDirection = config.read_direction
