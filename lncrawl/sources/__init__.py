# -*- coding: utf-8 -*-
"""
Files are auto-imported by the app, if it meets these conditions:
    - file ends with .py extension
    - file does not starts with an underscore
    - contains a class that extends `lncrawl.app.scraper.scraper`
    - `base_urls` contains a list of urls supported by the scraper

For example, see any of the files inside this directory.
"""

from typing import Mapping

# Add rejected urls with reason of rejection here
rejected_sources: Mapping[str, str] = {}
