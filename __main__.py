#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lncrawl.app.config import CONFIG
from lncrawl.app.models import Author, Chapter, Language, Novel, TextDirection, Volume

CONFIG.save()
print(CONFIG.work_directory)
print(CONFIG.logging.root_log_level)
print(CONFIG.logging.root_log_handlers)

print(Chapter(Volume(Novel('http://www.google.com'), 2), 10))
print(Author('Sudipto Chandra', Author.Type.AUTHOR))
print(Language.ENGLISH)
