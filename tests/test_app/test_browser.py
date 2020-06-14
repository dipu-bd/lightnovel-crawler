# -*- coding: utf-8 -*-

import pytest
import hashlib
import json
import time
from urllib.parse import parse_qsl

import requests
import responses

from lncrawl.app.browser import Browser

test_url = 'http://test.domain'


class TestBrowser:

    def test_browser_instance(self):
        b = Browser()
        assert b is not None

    @responses.activate
    def test_get_json(self):
        b = Browser()
        json_data = {"message": "ok", "unicode_test": u"বাংলা"}
        responses.add(responses.GET,
                      test_url,
                      status=204,
                      json=json_data)
        res = b.get(test_url)
        assert res is not None
        assert res.url == test_url
        assert res.encoding is not None
        assert res.response.status_code == 204
        assert res.json == json_data
        assert res.soup is not None
        assert res.soup.body.text == json.dumps(json_data)

    @responses.activate
    def test_get_soup(self):
        b = Browser()
        responses.add(responses.GET,
                      test_url,
                      status=203,
                      body='<html><head></head><body><p>secret text</p></body></html>')
        res = b.get(test_url)
        assert res is not None
        assert res.response.status_code == 203
        assert res.encoding is not None
        assert res.json is None
        assert res.soup is not None
        assert res.soup.find('p').text == 'secret text'

    @responses.activate
    def test_get_empty_content(self):
        b = Browser()
        responses.add(responses.GET,
                      test_url,
                      status=200)
        res = b.get(test_url)
        assert res is not None
        assert res.response.status_code == 200
        assert res.encoding is not None
        assert res.json is None
        assert res.soup is not None
        assert res.soup.body.text == ''

    @responses.activate
    def test_get_bad_status(self):
        b = Browser()
        responses.add(responses.GET,
                      test_url,
                      status=500)
        res = b.get(test_url)
        assert res is not None
        with pytest.raises(requests.HTTPError):
            assert res.response is not None

    @responses.activate
    def test_get_headers(self):
        b = Browser()
        test_headers = {'some': 'header', 'another': '2'}
        responses.add(responses.GET,
                      test_url,
                      adding_headers=test_headers)
        res = b.get(test_url)
        assert res is not None
        for key, val in test_headers.items():
            assert key in res.response.headers
            assert res.response.headers[key] == val

    @responses.activate
    def test_get_cookies(self):
        b = Browser()

        # First set of cookie
        headers = [
            ('Set-Cookie', 'test=cookie; path=/; HttpOnly'),
            ('Set-Cookie', 'alpha=test; path=/; HttpOnly'),
        ]
        responses.add(responses.GET,
                      test_url,
                      adding_headers=headers)
        res = b.get(test_url)
        assert res is not None
        assert res.response.cookies is not None
        assert res.response.cookies.get('alpha') == 'test'
        assert res.response.cookies.get('test') == 'cookie'
        assert b.cookies.get('alpha') == 'test'
        assert b.cookies.get('test') == 'cookie'

        # Second set of cookie
        headers = [
            ('Set-Cookie', 'test=second; path=/; HttpOnly'),
            ('Set-Cookie', 'another=fall; path=/; HttpOnly'),
        ]
        responses.replace(responses.GET,
                          test_url,
                          headers=headers)
        res = b.get(test_url)
        assert res is not None
        assert res.url == test_url
        assert res.response.cookies is not None
        assert res.response.cookies.get('test') == 'second'
        assert res.response.cookies.get('another') == 'fall'
        assert b.cookies.get('alpha') == 'test'
        assert b.cookies.get('test') == 'second'
        assert b.cookies.get('another') == 'fall'
