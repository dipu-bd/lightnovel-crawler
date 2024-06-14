# -*- coding: utf-8 -*-
import logging
import re
from typing import List
from urllib.parse import urlparse

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter, SearchResult, Volume

logger = logging.getLogger(__name__)
search_url = (
    "https://novelasligeras.net/?post_type=product&title=1&excerpt=1&content=0&categories=1&attributes=1"
    "&tags=1&sku=0&orderby=title-DESC&ixwps=1&s=%s"
)


class NovelasLigerasCrawler(Crawler):
    base_url = ["https://novelasligeras.net/"]
    has_manga = False
    has_mtl = False

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(["Publicidad"])
        self.cleaner.bad_css.update(["div[style]"])

    def login(self, email: str, password: str) -> None:
        # TODO optimize login headers
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "TE": "Trailers",
            "Referer": "https://novelasligeras.net/index.php/suscripcion-ingresar/",
        }
        data = {
            "log": email,
            "pwd": password,
            "wp-submit": "Acceder",
            "redirect_to": "https://novelasligeras.net/index.php/suscripcion-cuenta-v2/",
            "mepr_process_login_form": "true",
            "mepr_is_login_page": "true",
            "testcookie": "1",
        }
        self.post_response(self.base_url[0], data=data, headers=header)

    def search_novel(self, query) -> List[SearchResult]:
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".wf-cell[data-post-id]"):
            title = tab.attrs["data-name"]
            rating_element = tab.select_one(".star-rating")
            rating = "N/A"
            if rating_element:
                rating = rating_element.attrs["aria-label"]
            url_element = tab.select_one(".alignnone")
            url = url_element.attrs["href"]
            results.append(
                SearchResult(
                    title=title.strip(),
                    url=self.absolute_url(url),
                    info="Clasificación: %s" % rating,
                )
            )

        return results

    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.product_title")
        assert possible_title, "Sin título"
        self.novel_title = possible_title.text.strip()

        possible_author = soup.select_one(
            'tr.woocommerce-product-attributes-item--attribute_pa_escritor a[rel="tag"]'
        )
        if possible_author:
            self.novel_author = possible_author.text.strip()

        possible_cover = soup.select_one('meta[property="og:image"]')
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover["content"])

        synopsis = soup.select_one(".woocommerce-product-details__short-description")
        if synopsis:
            self.novel_synopsis = synopsis.text

        hostname = urlparse(self.novel_url).hostname or ""
        pattern = re.escape(hostname) + "/index.php" + r"/\d{4}/\d{2}/\d{2}/"

        volume_pattern = r"-volumen-(\d+)-"

        logger.debug("pattern = %s", pattern)

        last_vol_id = 0
        chapters_count = 0

        for a in soup.select(
            ".wpb_wrapper a:not([id],[title],[href$='suscripciones/'],[href*='patreon'],[href*='paypal'])"
        ):
            if not re.search(pattern, a["href"]):
                continue
            chapters_count += 1
            chap_id = chapters_count

            match = re.search(volume_pattern, a["href"])
            if match:
                vol_id = int(match.group(1))
                last_vol_id = vol_id
            else:
                vol_id = last_vol_id

            vol_present = any(vol["id"] == vol_id for vol in self.volumes)
            vol_title = f"Volumen {vol_id}"
            if not vol_present:
                self.volumes.append(Volume(id=vol_id, title=vol_title))

            temp_title = a.text.strip()
            temp_title = re.sub(r"\bCapitulo\b", "Capítulo", temp_title)

            if "Parte" in temp_title and "Capítulo" in temp_title:
                partes = temp_title.split(" – ")
                title = " – ".join(partes[::-1])
            else:
                title = temp_title

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    title=title,
                    url=self.absolute_url(a["href"]),
                    volume=vol_id,
                    volume_title=vol_title,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        if soup.select_one(".wpb_text_column > div:nth-child(1)"):
            text = soup.select_one(".wpb_text_column > div:nth-child(1)")
            return self.cleaner.extract_contents(text)
        return "--Error al cargar el capítulo--"
