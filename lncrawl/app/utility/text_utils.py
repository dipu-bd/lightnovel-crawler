# -*- coding: utf-8 -*-

import re

re_latin_only = re.compile('[^\u0000-\u00FF]', re.UNICODE)


class TextUtils:

    @staticmethod
    def latin_only(text: str) -> str:
        return re_latin_only.sub('', text or '')
