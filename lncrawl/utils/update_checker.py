import atexit
import json
import logging
import os
import threading

import requests
from packaging import version

from ..assets.icons import Icons
from ..assets.version import get_value
from ..core.display import new_version_news

logger = logging.Logger('UPDATE_CHECK')

app_name = ''
pypi_short_url = 'https://rebrand.ly/lncrawl-pip'
current_version = version.parse(get_value())
update_file = os.path.expanduser('~/.lncrawl/update.json')

if Icons.isWindows:
    user_agent = 'Mozilla/5.0 (Windows NT 10.0) LightnovelCrawler/' + get_value()
elif Icons.isLinux:
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) LightnovelCrawler/' + get_value()
elif Icons.isMac:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3) LightnovelCrawler/' + get_value()
else:
    user_agent = 'Mozilla/5.0 LightnovelCrawler/' + get_value()
# end if


def check_update_in_background():
    try:
        res = requests.get(
            pypi_short_url,
            stream=True,
            allow_redirects=True,
            headers={
                'user-agent': user_agent,
                'accept': 'application/json',
            }
        )
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
    try:
        with open(update_file, encoding='utf8') as fp:
            data = json.load(fp)
            latest_version = version.parse(data['info']['version'])
            if latest_version > current_version:
                new_version_news(str(latest_version))
            # end if
        # end witrh
    except Exception as e:
        logger.debug("Failed to check for update. %s", str(e))
    # end try

    # Run upload file resolver in background
    threading.Thread(target=check_update_in_background, daemon=True).start()
# end def
