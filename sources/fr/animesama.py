# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class animesama(Crawler):
    has_manga = True
    base_url = [
        "https://anime-sama.fr/",
    ]

    def search_novel(self, query):
        search_url = f"{self.home_url}template-php/defaut/fetch.php"
        data = self.submit_form(search_url, {"query": query})
        soup = self.make_soup(data)

        results = []
        for a in soup.select("a"):
            results.append(
                {
                    "title": a.select_one("h3").text,
                    "url": a["href"],
                    "info": a.select_one("p").text,
                }
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("#titreOeuvre")
        assert possible_title, "Could not find title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("#coverOeuvre")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # No author info

        before_synopsis = soup.find("h2", text="Synopsis")
        if before_synopsis and before_synopsis.find_next("p"):
            self.novel_synopsis = before_synopsis.find_next("p").text.strip()
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        before_tags = soup.find("h2", text="Genres")
        if before_tags and before_tags.find_next("a"):
            self.novel_tags = before_tags.find_next("a").text.strip().split(", ")
        logger.info("Novel tags: %s", self.novel_tags)

        # anime-sama group all manga and spin-off in one page. We have no way to search them separately,
        # so we just get everything and consider spin-off as volumes
        before_manga = soup.find("h2", text="Manga")
        script = before_manga.find_next("script")
        if not script:
            raise Exception("No chapters found")

        mangas = {}
        pattern = re.compile(r"""panneauScan\("(.+)", "(.+)"\);""")
        for line in script.text.splitlines():
            search = pattern.search(line)
            if search:
                name = search.group(1)
                url = search.group(2)
                if (url) and (name) and (name != "nom"):
                    mangas[name] = url

        # All chatper content are on the same place from a js file
        # So we get everything now and we will generate the chapters later in download_chapter_body
        # all_content[x] is a volume
        # all_content[x][y] is a chapter
        # all_content[x][y][z] is a page
        self.all_content = []
        for manga in mangas.values():
            manga_url = f"{self.novel_url}/{manga}/"
            soup = self.get_soup(manga_url)
            url_request = soup.select_one('script[src*="episodes.js?filever="]')["src"]
            js_code = self.get_response(f"{manga_url}{url_request}").text.replace(
                "\r\n", "\n"
            )
            # JS looks like this:
            # var eps2= [
            # 'https://drive.google.com/uc?export=view&id=19eF3IFONG4fe_jOJStYjH4ojAx3og9yr',
            # ];
            # var eps1= [
            # 'https://drive.google.com/uc?export=view&id=1Tok8UsaSSjfWj7kGiMxFs2TIM4Nc2nn9',
            # 'https://drive.google.com/uc?export=view&id=1M4E7EIb37lLL2ayVlOIK_okq-Y1DSLu1',
            # ];
            # With eps{x} not in order

            group_var = re.findall(r"(var \w+=\s*\[\n(?:'[^']*'(?:,\n)?)+\];)", js_code)
            url_lists = []
            for var in group_var:
                name = int(re.search(r"var eps(\d+)", var).group(1))
                urls = re.findall(r"'([^']*)'", var)
                url_lists.append([name, urls])

            url_lists.sort(key=lambda x: x[0])
            self.all_content.append([x[1] for x in url_lists])

        self.volumes = [
            {"id": i, "title": title} for i, title in enumerate(mangas.keys())
        ]
        for vol_id, vol in enumerate(self.all_content):
            for chap_number in range(1, len(vol) + 1):

                # For exemple for demon slayer we have a volume named "Scans" (default name) for the main story
                # and a volume named "Spin-off Rengoku"
                # We want to write the volume name only if it is not the default one
                for volume in self.volumes:
                    if volume["id"] == vol_id:
                        vol_title = volume["title"]
                        break
                if vol_title == "Scans":
                    chap_title = f"Chapitre {chap_number}"
                else:
                    chap_title = f"{vol_title} chapitre {chap_number}"

                # There are no individual chapter url. Everything is on the same page and chapter are generated client side
                self.chapters.append(
                    {
                        "id": 1 + len(self.chapters),
                        "volume": vol_id,
                        "title": chap_title,
                    }
                )

    def download_chapter_body(self, chapter):
        list_of_img = self.all_content[chapter["volume"]][chapter["id"] - 1]
        return "".join([f'<img src="{src}" />' for src in list_of_img])
