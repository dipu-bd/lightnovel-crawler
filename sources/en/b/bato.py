# -*- coding: utf-8 -*-
import base64
import json
import logging
import re
from hashlib import md5

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
BLOCK_SIZE = 16
search_url = "https://bato.to/search?word=%s"

try:
    from Crypto.Cipher import AES
except ImportError:
    logger.info("Crypto not found. Run `pip install pycryptodome` to install.")


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


def _pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length) * length).encode()


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


class BatoCrawler(Crawler):
    has_manga = True
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
        "https://mangatoto.net/",
    ]

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for div in soup.select("#series-list > div"):
            a = div.select_one("a.item-title")

            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h3.item-title")
        assert possible_title, "Could not find title"

        self.novel_title = possible_title.text.strip()

        possible_image = soup.select_one(".attr-cover img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        author_b = soup.find("b", string="Authors:")

        if author_b and author_b.parent and author_b.parent.span:
            self.novel_author = author_b.parent.span.text.strip()

        logger.info("Author: %s", self.novel_author)

        for a in reversed(soup.select(".main a.chapt")):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text,
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        soup = soup.find("script", string=re.compile(r"const imgHttps = \["))

        img_list = json.loads(
            re.search(r"const imgHttps = (.*);", soup.text).group(1)
        )

        bato_pass = decode_pass(
            re.search(r"const batoPass = (.*);", soup.text).group(1)
        )

        bato_word = re.search(r"const batoWord = (.*);", soup.text).group(1).strip('"')

        # looks like some kind of "access" GET args that may be necessary, not always though
        query_args = json.loads(decrypt(bato_word, bato_pass).decode())

        # so if it ends up empty or mismatches, just ignore it and return the img list instead
        if len(query_args) != len(img_list):
            image_urls = [
                f'<img src="{img}" alt="img">' for img in img_list
            ]
        else:
            image_urls = [
                f'<img src="{img}?{args}">' for img, args in zip(img_list, query_args)
            ]

        return "<p>" + "</p><p>".join(image_urls) + "</p>"
