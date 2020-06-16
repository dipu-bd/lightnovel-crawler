# -*- coding: utf-8 -*-

from typing import List, Mapping, Union
from urllib.parse import *


class UrlUtils:
    @staticmethod
    def join(base: str, url: str):
        '''Make provided url absolute to the base url'''
        base_parsed = urlparse(base)
        parse_result = urlparse(url)
        scheme, netloc, path, params, query, fragment = parse_result
        if not scheme:
            scheme = base_parsed.scheme
            if not netloc:
                netloc = base_parsed.netloc
                if not params:
                    params = base_parsed.params
                if not path:
                    path = base_parsed.path
                elif not path.startswith('/'):
                    path = base_parsed.path + '/' + path

        final_result = ParseResult(scheme, netloc, path, params, query, fragment)
        return urlunparse(final_result)

    @staticmethod
    def format(url: str,
               path: Union[str, List[str]] = None,
               query: Union[str, Mapping[str, str]] = None,
               fragment: List[str] = None) -> str:
        '''Append the extra parameters to the URL'''
        parse_result = urlparse(url)
        _scheme, _netloc, _path, _params, _query, _fragment = parse_result

        if query is not None:
            if isinstance(path, str):
                query = parse_qs(query, keep_blank_values=False)
            parsed_query = parse_qs(_query, keep_blank_values=True)
            for k, v in query.items():
                parsed_query.setdefault(k, [])
                parsed_query[k].append(v)
            _query = urlencode(parsed_query, doseq=True)

        if path is not None:
            if isinstance(path, str):
                path = [path]
            _path = '/'.join(path)

        if fragment is not None:
            _fragment = quote(fragment)

        final_result = ParseResult(_scheme, _netloc, _path, _params, _query, _fragment)
        return urlunparse(final_result)
