# -*- coding: utf-8 -*-
import json
import logging
import os
import platform
import sys
from datetime import datetime
from urllib.parse import urlencode

import requests

from ...assets.user_agents import user_agents

logger = logging.getLogger(__name__)

# Authentication for user filing issue
USERNAME = os.getenv('GITHUB_USERNAME')
# PASSWORD = os.getenv('GITHUB_PASSWORD')  # deprecated
TOKEN = os.getenv('GITHUB_TOKEN')  # must have read/write access to repo

# The repository to add this issue to
REPO_OWNER = 'dipu-bd'
REPO_NAME = 'lightnovel-crawler'

# Headers
headers = {
    "User-Agent": user_agents[0],
    "Authorization": "token %s" % TOKEN,
    "Accept": "application/vnd.github.golden-comet-preview+json"
}


def find_issues(labels=None):
    '''Returns list of issues by query'''
    # Url to get issues via GET
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)

    # Create a session without authentication
    session = requests.Session()

    # Create our issue
    data = {
        'labels': labels,
    }

    # Get issues
    r = session.get(url + '?' + urlencode(data), headers=headers)
    if r.ok:
        logger.info('Successfully retrieved issues')
        return r.json()
    else:
        logger.info('Failed to get issues: %s' % url)
        logger.debug('Response:\n%s\n' % r.content)
        return []
    # end if
# end def


def post_issue(title, body=None, labels=None):
    '''Create an issue on github.com using the given parameters.'''
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/import/issues' % (
        REPO_OWNER, REPO_NAME)

    # Create an authenticated session to create the issue
    session = requests.Session()
    # session.auth = (USERNAME, PASSWORD)

    # Create our issue
    payload = json.dumps({
        'issue': {
            'title': title,
            'body': body,
            'labels': labels,
        }
    })

    # Add the issue to our repository
    r = session.post(url, data=payload, headers=headers)
    if r.ok:
        logger.info('Successfully created Issue %s' % title)
    else:
        logger.info('Could not create Issue %s' % title)
        logger.debug('Response:\n%s\n' % r.content)
        raise Exception('Failed to create issue')
    # end if
# end def


def post_on_github(self, message):
    if sys.version_info.minor != 6:
        print('Not Python 3.6... skipping.')
        return
    # end if

    # Check if there is already an issue younger than a week
    issues = find_issues('bot-report')
    if len(issues):
        time = int(issues[0]['title'].split('~')[-1].strip())
        diff = datetime.utcnow().timestamp() - time
        if diff < 7 * 24 * 3600:
            print('Detected an open issue younger than a week... skipping.')
            return
        # end if
    # end if

    # Create new issue with appropriate label
    title = '[Test Bot][Python %d.%d][%s] Report ~ %s' % (
        sys.version_info.major,
        sys.version_info.minor,
        platform.system(),
        datetime.utcnow().strftime('%s')
    )
    post_issue(title, message, ['bot-report'])
# end def
