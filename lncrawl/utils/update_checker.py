# -*- coding: utf-8 -*-
import atexit
import json
import logging
import os
import threading

import cloudscraper
from packaging import version

from ..assets.version import get_value
from ..core.display import new_version_news

logger = logging.Logger('UPDATE_CHECK')

pypi_short_url = 'https://rebrand.ly/lncrawl-pip'
current_version = version.parse(get_value())
update_file = os.path.expanduser('~/.lncrawl/update.json')


def check_update_in_background():
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(pypi_short_url, stream=True)
        os.makedirs(os.path.dirname(update_file), exist_ok=True)
        with open(update_file, 'wb') as f:
            f.write(res.content)
        # end with
    except Exception as e:
        atexit.register(logger.debug, 'Failed to check for update', e)
    # end try
# end def


def check_updates():
    # Check the last update file
    if os.path.isfile(update_file):
        with open(update_file, encoding='utf8') as fp:
            data = json.load(fp)
            latest_version = version.parse(data['info']['version'])
            if latest_version > current_version:
                new_version_news(str(latest_version))
            # end if
        # end witrh
    # end if

    # Run upload file resolver in background
    threading.Thread(target=check_update_in_background, daemon=True).start()
# end def
