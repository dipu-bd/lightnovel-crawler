# -*- coding: utf-8 -*-

from src.app.browser import Browser


class TestBrowser:

    def test_browser_instance(self):
        b = Browser()
        assert b is not None
