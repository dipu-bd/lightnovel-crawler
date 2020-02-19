#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from src.app.models import *
from src.app.config import CONFIG

CONFIG.save()
print(CONFIG.defaults.work_directory)
print(CONFIG.logging.root_log_level)
print(CONFIG.logging.root_log_handlers)

print(Chapter(Volume(Novel('http://www.google.com'), 2), 10))
print(Author('Sudipto Chandra', Author.Type.AUTHOR))
print(Language.ENGLISH)
