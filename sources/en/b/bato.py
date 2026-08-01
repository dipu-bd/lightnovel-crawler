# -*- coding: utf-8 -*-
import base64
from hashlib import md5
import json
import logging
import re
from typing import Iterable

from Crypto.Cipher import AES

from lncrawl.core import Chapter, Novel, PageSoup, SearchResult, SoupTemplate

logger = logging.getLogger(__name__)
BLOCK_SIZE = 16
search_url = "https://wto.to/search?word=%s"


class BatoCrawler(SoupTemplate):
    has_manga = True
    can_search = True
    base_url = [
        "https://bato.to/",
        "https://battwo.com/",
        "https://mto.to/",
        "https://mangatoto.net/",
        "https://dto.to/",
        "https://batocc.com/",
        "https://batotoo.com/",
        "https://wto.to/",
        "https://mangatoto.com/",
        "https://comiko.net/",
        "https://batotwo.com/",
        "https://mangatoto.org/",
        "https://hto.to/",
    ]

    novel_title_selector = "h3.item-title"
    novel_cover_selector = ".attr-cover img"
    chapter_list_selector = ".main a.chapt"
    chapter_list_reverse = True

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        soup = self.scraper.get_soup(search_url % query.lower().replace(" ", "+"))
        return soup.select("#series-list > div")

    def parse_search_item(self, soup: PageSoup) -> SearchResult:
        a = soup.select_one("a.item-title")
        return SearchResult(title=a.text.strip(), url=self.absolute_url(a["href"]))

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.find("b", string="Authors:")
        if tag and tag.parent and tag.parent.span:
            novel.author = tag.parent.span.text.strip()

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(self.build_chapter_url(chapter))
        script = soup.find("script", string=re.compile(r"const imgHttps = \["))

        match = re.search(r"const imgHttps = (.*);", script.text)
        img_list = json.loads(match.group(1)) if match else []

        match = re.search(r"const batoPass = (.*);", script.text)
        bato_pass = decode_pass(match.group(1)) if match else ""

        match = re.search(r"const batoWord = (.*);", script.text)
        bato_word = match.group(1).strip('"') if match else ""

        # looks like some kind of "access" GET args that may be necessary, not always though
        query_args = json.loads(decrypt(bato_word, bato_pass).decode())

        # so if it ends up empty or mismatches, just ignore it and return the img list instead
        if len(query_args) != len(img_list):
            image_urls = [f'<img src="{img}" alt="img">' for img in img_list]
        else:
            image_urls = [f'<img src="{img}?{args}">' for img, args in zip(img_list, query_args)]

        chapter.body = "<p>" + "</p><p>".join(image_urls) + "</p>"


def decode_pass(code):
    code = code.replace("!+[]", "1").replace("!![]", "1").replace("[]", "0")
    code = code.lstrip("+").replace("(+", "(").replace(" ", "")
    code = code.replace("+((1+[+1]+(1+0)[1+1+1]+[1+1]+[+0])+0)[+1]+", ".")
    code = code.replace("]+[", " ").replace("[", "").replace("]", "")

    res = ""
    for num_part in code.split("."):
        for num in num_part.split():
            res += str(num.count("1"))
        res += "."

    return res.strip(".")


def _unpad(data):
    return data[: -(data[-1] if isinstance(data[-1], int) else ord(data[-1]))]


def _bytes_to_key(data, salt, output=48):
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]


def decrypt(encrypted, passphrase):
    passphrase = passphrase.encode()

    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = _bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return _unpad(aes.decrypt(encrypted[16:]))
