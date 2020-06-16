# -*- coding: utf-8 -*-

from urllib import parse


class UrlUtils:
    @staticmethod
    def join(base: str, url: str):
        base_parsed = parse.urlparse(base)
        parse_result = parse.urlparse(url)
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
        final_result = parse.ParseResult(scheme, netloc, path, params, query, fragment)
        return parse.urlunparse(final_result)
