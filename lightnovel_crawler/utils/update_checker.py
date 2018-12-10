import requests
from ..assets.version import get_value

def check_updates():
    current = get_value()
    res = requests.get('https://pypi.org/pypi/lightnovel-crawler/json')
    latest = res.json()['info']['version']
    return latest if current != latest else None
# end def
