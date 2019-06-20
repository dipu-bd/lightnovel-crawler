# -*- coding: utf-8 -*-
import os
import json
import requests

# Authentication for user filing issue
USERNAME = os.environ['GITHUB_USERNAME']
PASSWORD = os.environ['GITHUB_PASSWORD']

# The repository to add this issue to
REPO_OWNER = 'dipu-bd'
REPO_NAME = 'lightnovel-crawler'


def post(title, body=None, labels=None):
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
        print('Successfully created Issue {0:s}'.format(title))
    else:
        print('Could not create Issue {0:s}'.format(title))
        print('Response:', r.content)
# end def
