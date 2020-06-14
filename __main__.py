#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lncrawl.app.config import CONFIG
from lncrawl.app.models import *

print(CONFIG.get('browser/parser/cloudscraper'))
print(CONFIG.get('logging/version'))
print(CONFIG.get('logging/loggers/level'))


print(Language.ENGLISH)
print(Author('Sudipto Chandra', AuthorType.AUTHOR))
print(Chapter(Volume(Novel('http://www.google.com'), 2), 10))
