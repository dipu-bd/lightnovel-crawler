# -*- coding: utf-8 -*-
import json
import logging
import re

from pyease_grpc import RpcSession

from lncrawl.core.exeptions import FallbackToBrowser
from lncrawl.models import Chapter, Volume
from lncrawl.templates.browser.basic import BasicBrowserTemplate
from lncrawl.webdriver.elements import By

logger = logging.getLogger(__name__)


class WuxiaComCrawler(BasicBrowserTemplate):
    base_url = [
        "https://www.wuxiaworld.com/",
    ]

    def initialize(self):
        #self.headless = True
        self.api_url = "https://api2.wuxiaworld.com"
        self.grpc = RpcSession.from_descriptor(WUXIWORLD_PROTO)
        self.grpc._session = self.scraper
        self.cleaner.bad_css.clear()
        self.cleaner.bad_tags.add("hr")
        self.bearer_token = None
        self.cleaner.unchanged_tags.update(["span"])
        self.start_download_chapter_body_in_browser = False
        self.localstorageuser = 'oidc.user:https://identity.wuxiaworld.com:wuxiaworld_spa'

    def login(self, email: str, password: str) -> None:
        # Login now will use Bearer Token if supplied as main login method,
        # and if username used it will exctract Bearer Token and use it for further login process
        if email == 'Bearer':
            logger.debug("login type: %s", email)
            self.bearer_token = email + " " + password
        else:
            logger.debug("login type: Email(%s)", email)
            self.init_browser()
            self.visit('https://www.wuxiaworld.com/manage/profile/')
            self.browser.wait("h6 button")
            self.browser.find("h6 button").click()
            self.browser.wait("input#Username")
            self.browser.find("input#Username").send_keys(email)
            self.browser.find("input#Password").send_keys(password)
            self.browser.find("button").click()
            try:
                # Testing if logging has succeeded
                self.browser.wait("//h2[normalize-space()='Your Profile']", By.XPATH, 10)
                self.browser.find("//h2[normalize-space()='Your Profile']", By.XPATH)
                storage = LocalStorage(self.browser._driver)
                if storage.has(self.localstorageuser):
                    self.bearer_token = '{token_type} {access_token}'.format(**json.loads(storage[self.localstorageuser]))
            except Exception as e:
                logger.debug("login Email: Failed", e)

    def read_novel_info_in_scraper(self) -> None:
        slug = re.findall(r"/novel/([^/]+)", self.novel_url)[0]
        logger.debug("Novel slug: %s", slug)

        response = self.grpc.request(
            f"{self.api_url}/wuxiaworld.api.v2.Novels/GetNovel",
            {"slug": slug},
            headers={
                "origin": self.home_url,
                "referer": self.novel_url,
                "authorization": self.bearer_token,
            },
        )

        assert response.single
        novel = response.single["item"]
        logger.info("Novel details: %s", novel)

        self.novel_title = novel["name"]
        logger.info("Novel title = %s", self.novel_title)

        self.novel_cover = novel["coverUrl"]
        logger.info("Novel cover = %s", self.novel_cover)

        self.novel_author = ", ".join(
            [
                f"Author: {novel.get('authorName', 'N/A')}",
                f"Translator: {novel.get('translatorName', 'N/A')}",
            ]
        )
        logger.info("Novel author = %s", self.novel_author)

        advance_chapter_allowed = 0
        try:
            response = self.grpc.request(
                f"{self.api_url}/wuxiaworld.api.v2.Subscriptions/GetSubscriptions",
                {"novelId": novel["id"]},
                headers={"authorization": self.bearer_token},
            )

            subscriptions = response.single["items"]
            logger.debug("User subscriptions: %s", subscriptions)
            for subscription in subscriptions:
                if "sponsor" in subscription["plan"]:
                    advance_chapter_allowed = subscription["plan"]["sponsor"][
                        "advanceChapterCount"
                    ]
        except Exception as e:
            logger.debug("Failed to acquire subscription details. %s", e)

        response = self.grpc.request(
            f"{self.api_url}/wuxiaworld.api.v2.Chapters/GetChapterList",
            {"novelId": novel["id"]},
            headers={"authorization": self.bearer_token},
        )
        assert response.single

        volumes = response.single["items"]
        for group in sorted(volumes, key=lambda x: x.get("order", 0)):
            vol_id = len(self.volumes) + 1
            self.volumes.append(
                Volume(
                    id=vol_id,
                    title=group["title"],
                )
            )

            for chap in group["chapterList"]:
                chap_id = len(self.chapters) + 1
                if not chap["visible"]:
                    continue

                is_free = chap["pricingInfo"]["isFree"]
                if not is_free and chap["sponsorInfo"]["advanceChapter"]:
                    adv_chap_num = chap["sponsorInfo"]["advanceChapterNumber"]
                    if adv_chap_num > advance_chapter_allowed:
                        continue

                chap_title = chap["name"]
                if chap.get("spoilerTitle"):
                    chap_title = f"Chapter {chap_id}"

                self.chapters.append(
                    Chapter(
                        id=chap_id,
                        volume=vol_id,
                        title=chap_title,
                        original_title=chap["name"],
                        chapterId=chap["entityId"],
                        url=f"https://www.wuxiaworld.com/novel/{slug}/{chap['slug']}",
                    )
                )

        if not self.chapters:
            raise FallbackToBrowser()

    def download_chapter_body_in_scraper(self, chapter: Chapter) -> str:
        response = self.grpc.request(
            f"{self.api_url}/wuxiaworld.api.v2.Chapters/GetChapter",
            {"chapterProperty": {"chapterId": chapter["chapterId"]}},
            headers={"authorization": self.bearer_token},
        )

        assert response.single, "Invalid response"
        content = response.single["item"]["content"]
        if "translatorThoughts" in response.single["item"]:
            content += "<hr/>"
            content += "<blockquote><b>Translator's Thoughts</b>"
            content += response.single["item"]["translatorThoughts"]
            content += "</blockquote>"

        content = re.sub(r'(background-)?color: [^\\";]+', "", content)
        return content

    def read_novel_info_in_browser(self) -> None:
        self.visit(self.novel_url)
        # Login
        if self.bearer_token:
            storage = LocalStorage(self.browser._driver)
            logger.debug("LocalStorage: %s", storage)
            if not storage.has(self.localstorageuser):
                token_type, token = self.bearer_token.split(" ", 1)
                storage[self.localstorageuser] = json.dumps({
                    "access_token": token,
                    "token_type": token_type,
                })
                logger.debug("LocalStorage: %s", storage)
                self.visit(self.novel_url)
            self.browser.wait("#novel-tabs #full-width-tab-2")
        self.browser.wait(".items-start h1, img.drop-shadow-ww-novel-cover-image")

        # Clear the annoying top menubar
        self.browser.find("header#header").remove()

        # Parse cover image and title
        img = self.browser.find("img.drop-shadow-ww-novel-cover-image")
        if img:
            self.novel_title = img.get_attribute("alt")
            self.novel_cover = self.absolute_url(img.get_attribute("src"))

        # Parse title from h1 if not available
        if not self.novel_title:
            h1 = self.browser.find(".items-start h1")
            if h1:
                self.novel_title = h1.text.strip()

        # Parse author
        author_tag = self.browser.find("//*[text()='Author:']", By.XPATH)
        if author_tag:
            author_tag = author_tag.find("following-sibling::*", By.XPATH)
        if author_tag:
            self.novel_author = author_tag.text.strip()

        # Open chapters menu (note: the order of tabs in novel info change whether if you are logged in or not)
        if len(self.browser.find_all('//*[starts-with(@id, "full-width-tab-")]', By.XPATH)) == 3:
            self.browser.click("#novel-tabs #full-width-tab-0")
            self.browser.wait("#full-width-tabpanel-0 .MuiAccordion-root")
        else:
            self.browser.click("#novel-tabs #full-width-tab-1")
            self.browser.wait("#full-width-tabpanel-1 .MuiAccordion-root")

        # Get volume list and a progress bar
        volumes = self.browser.find_all("#app .MuiAccordion-root")
        bar = self.progress_bar(
            total=len(volumes),
            desc="Volumes",
            unit="vol",
        )

        # Expand all volumes
        for index, root in enumerate(reversed(volumes)):
            root.scroll_into_view()
            root.click()

            nth = len(volumes) - index
            self.browser.wait(f"#app .MuiAccordion-root:nth-of-type({nth}) a[href]")

            tag = root.as_tag()
            head = tag.select_one(".MuiAccordionSummary-content")
            title = head.select_one("section span.font-set-sb18").text.strip()
            vol = Volume(
                id=len(self.volumes) + 1,
                title=title,
            )
            self.volumes.append(vol)

            for a in reversed(tag.select("a[href]")):
                data = json.loads(a["data-amplitude-params"])
                chap = Chapter(
                    volume=vol.id,
                    id=len(self.chapters) + 1,
                    url=self.absolute_url(a["href"]),
                    title=data["chapterTitle"],
                    chapterId=data["chapterId"],
                )
                self.chapters.append(chap)

            bar.update()

        # Close progress bar
        bar.close()

    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        # login
        if not self.start_download_chapter_body_in_browser:
            if self.bearer_token:
                self.visit('https://www.wuxiaworld.com/manage/profile/')
                storage = LocalStorage(self.browser._driver)
                logger.debug("LocalStorage: %s", storage)
                if not storage.has(self.localstorageuser):
                    token_type, token = self.bearer_token.split(" ", 1)
                    storage[self.localstorageuser] = json.dumps({
                        "access_token": token,
                        "token_type": token_type,
                    })
                    logger.debug("LocalStorage: %s", storage)
                    self.visit('https://www.wuxiaworld.com/manage/profile/')
                    try:
                        self.browser.wait("//h2[normalize-space()='Your Profile']", By.XPATH, 10)
                        self.browser.find("//h2[normalize-space()='Your Profile']", By.XPATH)
                    except Exception as e:
                        logger.debug("login Email: Failed", e)
            self.start_download_chapter_body_in_browser = True
        self.visit(chapter.url)
        try:
            # wait untill chapter fully loaded
            self.browser.wait("chapter-content", By.CLASS_NAME)
            if self.bearer_token:
                self.browser.wait("//button[normalize-space()='Favorite']", By.XPATH, 10)
                self.browser.find("//button[normalize-space()='Favorite']", By.XPATH)
        except Exception as e:
            logger.debug("error loading (%s)", str(chapter.url), e)
        content = self.browser.find("chapter-content", By.CLASS_NAME).as_tag()
        self.cleaner.clean_contents(content)
        return content.decode_contents()


# Class for reading localStorage from Browser
class LocalStorage:
    def __init__(self, driver) :
        self.driver = driver

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def items(self) :
        return self.driver.execute_script(
            "var ls = window.localStorage, items = {}; "
            "for (var i = 0, k; i < ls.length; ++i) "
            "  items[k = ls.key(i)] = ls.getItem(k); "
            "return items; "
        )

    def keys(self) :
        return self.driver.execute_script(
            "var ls = window.localStorage, keys = []; "
            "for (var i = 0; i < ls.length; ++i) "
            "  keys[i] = ls.key(i); "
            "return keys; "
        )

    def get(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def set(self, key, value):
        self.driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def has(self, key):
        return key in self.keys()

    def remove(self, key):
        self.driver.execute_script("window.localStorage.removeItem(arguments[0]);", key)

    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")

    def __getitem__(self, key) :
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return self.items().__iter__()

    def __repr__(self):
        return self.items().__str__()


WUXIWORLD_PROTO = json.loads(open('wuxiacom.proto').read())  # noqa: E501
