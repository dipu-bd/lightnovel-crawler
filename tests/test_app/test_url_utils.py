# -*- coding: utf-8 -*-

import pytest

from lncrawl.app.utility import UrlUtils


class TestUrlUtils:

    def testJoin(self):
        assert UrlUtils.join('http://some.url', 'path') == 'http://some.url/path'
        assert UrlUtils.join('http://some.url/path', '/over') == 'http://some.url/over'
        assert UrlUtils.join('http://some.url/path', 'follow') == 'http://some.url/path/follow'
        assert UrlUtils.join('http://some.url', '//other.url') == 'http://other.url'
        assert UrlUtils.join('http://some.url/path', '//other.url') == 'http://other.url'
        assert UrlUtils.join('http://some.url/path', '//other.url/over') == 'http://other.url/over'
        assert UrlUtils.join('http://some.url/pre?q=uery', 'post') == 'http://some.url/pre/post'
        assert UrlUtils.join('http://some.url', 'http://full.url') == 'http://full.url'
        assert UrlUtils.join('http://some.url/any', 'http://full.url/pat') == 'http://full.url/pat'
        assert UrlUtils.join('http://some.url', 'http://full.url/s/p') == 'http://full.url/s/p'
