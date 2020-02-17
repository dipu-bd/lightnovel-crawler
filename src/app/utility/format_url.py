# -*- coding: utf-8 -*-

from typing import Mapping, Union, List
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse


def reformat_url(url: str,
                 query: Mapping[str, str] = None,
                 path: Union[str, List[str]] = None,
                 fragment: List[str] = None) -> str:
    '''Re-format and append the extra parameters to the URL'''
    parsed_url = urlparse(url)

    if query is not None:
        parsed_query = parse_qs(parsed_url.query, keep_blank_values=True)
        for k, v in query.items():
            parsed_query.setdefault(k, [])
            parsed_query[k].append(v)
        parsed_url = parsed_url._replace(query=urlencode(parsed_query, True))

    if path is not None:
        if not isinstance(path, list):
            path = [path]
        parsed_url = parsed_url._replace(path='/'.join(path))

    if fragment is not None:
        parsed_url = parsed_url._replace(fragment=quote(fragment))

    return urlunparse(parsed_url)
