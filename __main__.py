#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from src_v3.app.config import Config

print(Config().defaults.work_directory)
print(Config().logging.root_log_level)
print(Config().logging.root_log_handlers)
Config().save()
