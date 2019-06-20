# -*- coding: utf-8 -*-
import json
import logging
import os
from urllib.parse import urlencode

import requests

logger = logging.getLogger('MAKE_GITHUB_ISSUE')

# Authentication for user filing issue
USERNAME = os.getenv('GITHUB_USERNAME')
PASSWORD = os.getenv('GITHUB_PASSWORD')

# The repository to add this issue to
REPO_OWNER = 'dipu-bd'
REPO_NAME = 'lightnovel-crawler'


def post_issue(title, body=None, labels=None):
    '''Create an issue on github.com using the given parameters.'''
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)

    # Create an authenticated session to create the issue
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    # Create our issue
    issue = {
        'title': title,
        'body': body,
        'labels': labels
    }

    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        logger.info('Successfully created Issue {0:s}'.format(title))
    else:
        logger.info('Could not create Issue {0:s}'.format(title))
        logger.debug('Response:\n%s\n' % r.content)
        raise Exception('Failed to create issue')
    # end if
# end def


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
    r = session.get(url + '?' + urlencode(data))
    if 200 <= r.status_code <= 300:
        logger.info('Successfully retrieved issues')
        return r.json()
    else:
        logger.info('Failed to get issues: %s' % url)
        logger.debug('Response:\n%s\n' % r.content)
        return []
    # end if
# end def
