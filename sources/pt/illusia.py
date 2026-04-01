# -*- coding: utf-8 -*-
"""
Illusia (illusia.com.br) — sem Selenium
- Busca via ?s=
- Lê metadados da história
- Lista capítulos pela REST API do WordPress (wp-json/wp/v2/fcn_chapter) com paginação
- Atribui volumes lendo a estrutura da página HTML (map: URL do capítulo -> volume)
"""

import logging
import re
from urllib.parse import urljoin

from lncrawl.core import Chapter, LegacyCrawler, PageSoup, Volume

logger = logging.getLogger(__name__)
SEARCH_URL = "https://illusia.com.br/?s=%s&post_type=wp-manga"


class Illusia(LegacyCrawler):
    base_url = "https://illusia.com.br/"

    # ----------------------- BUSCA -----------------------
    def search_novel(self, query):
        q = query.lower().strip().replace(" ", "+")
        soup = self.get_soup(SEARCH_URL % q)
        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            if not a:
                continue
            latest = tab.select_one(".latest-chap .chapter a")
            votes = tab.select_one(".rating .total_votes")
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s"
                    % (
                        latest.text.strip() if latest else "N/A",
                        votes.text.strip() if votes else "0",
                    ),
                }
            )
        return results

    # ------------------- INFO DA NOVEL -------------------
    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # --- Título robusto (Fictioneer) ---
        h1 = soup.select_one(".post-title h1") or soup.select_one("h1.entry-title")
        if h1:
            for sp in h1.select("span"):
                sp.extract()
            self.novel_title = h1.get_text(strip=True)
        if not self.novel_title:
            ogt = soup.select_one('meta[property="og:title"]')
            if ogt and ogt.get("content"):
                self.novel_title = ogt["content"].strip()
        if not self.novel_title and soup.title:
            self.novel_title = soup.title.get_text(strip=True).split(" – Illusia")[0].strip()
        if not self.novel_title:
            raise Exception("Título não encontrado")

        # --- Capa ---
        og = soup.select_one('meta[property="og:image"]')
        if og and og.get("content"):
            self.novel_cover = self.absolute_url(og["content"])
        else:
            img = soup.select_one(".summary_image img")
            if img:
                self.novel_cover = self.absolute_url(img.get("data-src") or img.get("src"))

        # --- Autor(es) ---
        authors = [a.get_text(strip=True) for a in soup.select(".author-content a")]
        if not authors:
            # fallback via meta tags
            for meta in soup.select('meta[property="article:author"]'):
                href = meta.get("content") or ""
                name = href.rstrip("/").split("/")[-1].replace("-", " ").title()
                if name:
                    authors.append(name)
        self.novel_author = ", ".join(dict.fromkeys([a for a in authors if a]))

        # --- Descobrir story_id pela tag JSON do WP ---
        story_id = None
        for link in soup.select('link[rel="alternate"][type="application/json"]'):
            href = link.get("href") or ""
            m = re.search(r"/wp-json/wp/v2/fcn_story/(\d+)", href)
            if m:
                story_id = m.group(1)
                break
        if not story_id:
            m = re.search(r"story_id=(\d+)", soup.decode())
            if m:
                story_id = m.group(1)

        # 1) Pega todos os capítulos via REST (rápido; sem volumes)
        if not story_id:
            raise Exception("story_id não encontrado")
        rest_ok = self._load_chapters_via_rest(story_id)
        if not rest_ok:
            # fallback bruto: varrer HTML (lento, mas funciona)
            self._load_chapters_from_html(soup)
            return

        # 2) Mapear volumes pelo HTML e reatribuir nos capítulos
        vol_list, url_to_vol = self._extract_volume_map_from_html(soup)
        if vol_list:
            # Reindexar capítulos para aplicar volume correto
            new_chapters = []
            for idx, ch in enumerate(self.chapters, start=1):
                vol_id = url_to_vol.get(ch["url"], 1)
                new_chapters.append(
                    {
                        "id": idx,
                        "volume": vol_id,
                        "title": ch["title"],
                        "url": ch["url"],
                    }
                )
            self.chapters = new_chapters
            self.volumes = vol_list
            self._set_display_numbers()
        else:
            # se não conseguir detectar volumes, mantém Volume 1
            if not self.volumes:
                self.volumes = [Volume(id=1, title="Volume 1")]
                self._set_display_numbers()

    # --------------- CONTEÚDO DO CAPÍTULO ---------------
    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one(".reading-content") or soup.select_one(".entry-content") or soup.select_one("article")
        return self.cleaner.extract_contents(content)

    # ==================== HELPERS ========================

    def _set_display_numbers(self) -> None:
        """Atribui um índice de exibição sequencial (1,2,3...) para cada volume.

        Não altera títulos; apenas adiciona 'display_number' no dict de cada volume."""
        try:
            for i, v in enumerate(self.volumes or [], start=1):
                if isinstance(v, (dict, Volume)):
                    v["display_number"] = i
        except Exception:
            pass

    def _load_chapters_via_rest(self, story_id: str) -> bool:
        """
        Usa o endpoint do WordPress para o CPT 'fcn_chapter':
        /wp-json/wp/v2/fcn_chapter?story={id}&per_page=100&page=N
        Retorna True se conseguiu carregar capítulos.
        """
        all_items = []
        page = 1
        per_page = 100
        base = urljoin(self.home_url, "wp-json/wp/v2/fcn_chapter")

        while True:
            params = {
                "story": story_id,
                "per_page": str(per_page),
                "page": str(page),
                # reduzir payload:
                "_fields": "link,title,menu_order,date",
            }
            try:
                r = self.scraper.get(base, params=params, headers={"Accept": "application/json"})
                if r.status_code == 400 and "rest_post_invalid_page_number" in r.text:
                    break
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                logger.debug("REST page %s falhou: %s", page, e)
                break

            if not data:
                break

            for it in data:
                link = it.get("link")
                t_html = it.get("title", {}).get("rendered", "") or ""
                t_text = PageSoup.create(t_html, parser="html.parser").get_text(strip=True)
                order = it.get("menu_order", 0)
                all_items.append((order, t_text, self.absolute_url(link)))

            page += 1
            if page > 500:  # proteção
                break

        if not all_items:
            return False

        # Ordena por menu_order (quando disponível), depois por link
        all_items.sort(key=lambda x: (x[0], x[2]))
        self.chapters = []
        for idx, (_, title, link) in enumerate(all_items, start=1):
            self.chapters.append(Chapter(id=idx, volume=1, title=title, url=link))
        self.volumes = [Volume(id=1, title="Volume 1")]
        logger.info("Capítulos via REST: %d", len(self.chapters))
        return True

    def _extract_volume_map_from_html(self, soup: PageSoup):
        """
        Lê a página da obra e extrai:
          - lista de volumes (na ordem em tela) -> [{"id": n, "title": "..."}]
          - mapa URL -> volume_id (para reatribuir capítulos)
        A heurística:
          - procura elementos cujo texto começa com "Volume" (a/h2/h3/div/span)
          - usa o <li> pai como container
          - dentro dele, pega <a href> que apontem para capítulos do mesmo slug
        """
        vol_list = []
        url_to_vol = {}

        novel_root = self.novel_url.rstrip("/") + "/"

        # pega todos elementos possíveis com texto "Volume ..."
        candidates = []
        for sel in ["a", "h2", "h3", "div", "span", "p", "strong"]:
            for el in soup.select(sel):
                txt = el.get_text(" ", strip=True)
                if not txt:
                    continue
                if txt.lower().startswith("volume"):
                    candidates.append(el)

        # dedup preservando ordem
        seen_ids = set()
        ordered = []
        for el in candidates:
            pid = id(el)
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
            ordered.append(el)

        volume_index = 0
        for el in ordered:
            li = el.find_parent("li")
            if not li:
                # alguns temas usam <div> como container
                li = el.find_parent(["div", "section", "article"])
            if not li:
                continue

            vol_title = el.get_text(" ", strip=True)
            if not vol_title or len(vol_title) < 4:
                continue

            volume_index += 1
            vol_list.append({"id": volume_index, "title": vol_title})

            anchors = li.select("a[href]")
            for a in anchors:
                href = (a.get("href") or "").strip()
                if not href:
                    continue
                if not href.startswith(novel_root) or href == novel_root:
                    continue
                url_to_vol[self.absolute_url(href)] = volume_index

        # EXTRA: bloco "Extras"
        for el in soup.find_all(string=True):
            txt = (el.strip() if isinstance(el, str) else "").lower()
            if txt == "extras":
                cont = el.parent if hasattr(el, "parent") else None
                if cont:
                    parent = cont.find_parent(["li", "div", "section", "article"]) or cont
                    anchors = parent.select("a[href]")
                    if anchors:
                        volume_index += 1
                        vol_list.append({"id": volume_index, "title": "Extras"})
                        for a in anchors:
                            href = (a.get("href") or "").strip()
                            if href and href.startswith(novel_root) and href != novel_root:
                                url_to_vol[self.absolute_url(href)] = volume_index
                break

        # saneamento: se não achou nada, devolve vazio (caller mantém Volume 1)
        if not vol_list:
            return [], {}
        return vol_list, url_to_vol

    def _load_chapters_from_html(self, soup: PageSoup) -> None:
        """
        Fallback se REST falhar: extrai volumes e capítulos direto do HTML
        (pode ser mais lento).
        """
        self.chapters = []
        self.volumes = []

        vol_list, url_to_vol = self._extract_volume_map_from_html(soup)
        if not vol_list:
            # varredura genérica (pouco provável precisar)
            novel_root = self.novel_url.rstrip("/") + "/"
            anchors = soup.select("a[href]")
            seen = set()
            chap_id = 0
            for an in anchors:
                href = (an.get("href") or "").strip()
                if not href or not href.startswith(novel_root) or href == novel_root:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                title = an.get_text(" ", strip=True) or an.get("title") or an.get("aria-label") or href
                chap_id += 1
                self.chapters.append(Chapter(id=chap_id, volume=1, title=title, url=self.absolute_url(href)))
            if self.chapters and not self.volumes:
                self.volumes = [Volume(id=1, title="Volume 1")]
                self._set_display_numbers()
            return

        # Construir capítulos na ordem dos volumes + ordem dos links
        chap_id = 0
        novel_root = self.novel_url.rstrip("/") + "/"
        for vol in vol_list:
            self.volumes.append(vol)

        # coletar todos os links de capítulo da página, na ordem de exibição
        anchors = soup.select("a[href]")
        ordered_links = []
        seen = set()
        for a in anchors:
            href = (a.get("href") or "").strip()
            if not href or not href.startswith(novel_root) or href == novel_root:
                continue
            url = self.absolute_url(href)
            if url in seen:
                continue
            seen.add(url)
            ordered_links.append((a, url))

        for a, url in ordered_links:
            vol_id = url_to_vol.get(url)
            if not vol_id:
                continue  # ignora links fora dos blocos de volume
            title = a.get_text(" ", strip=True) or a.get("title") or a.get("aria-label") or url
            chap_id += 1
            self.chapters.append(Chapter(id=chap_id, volume=vol_id, title=title, url=url))
        self._set_display_numbers()
        logger.info("Capítulos via HTML: %d | Volumes: %d", len(self.chapters), len(self.volumes))
