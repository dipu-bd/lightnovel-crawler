#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from src_v3.app.models import *
from src_v3.app.config import Config

Config().save()
print(Config().defaults.work_directory)
print(Config().logging.root_log_level)
print(Config().logging.root_log_handlers)

print(Chapter(Volume(Novel('http://www.google.com'), 2), 10))
print(Author('Sudipto Chandra', Author.Type.AUTHOR))
print(Language.ENGLISH)
