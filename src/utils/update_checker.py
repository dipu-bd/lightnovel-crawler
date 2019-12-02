#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

import requests

from ..assets.user_agents import user_agents
from ..assets.version import get_value
from ..core.display import new_version_news

logger = logging.Logger('UPDATE_CHECK')


def check_updates():
    try:
        logger.info('Checking latest version')
        pypi_short_url = 'http://bit.ly/2yYyFGd'
        headers = {'User-Agent': user_agents[0]}
        res = requests.get(pypi_short_url, verify=False,
                           headers=headers, timeout=2)
        latest_version = res.json()['info']['version']
        if get_value() != latest_version:
            new_version_news(latest_version)
        # end if
    except Exception:
        logger.warn('Failed to check for update')
    # end try
# end def
