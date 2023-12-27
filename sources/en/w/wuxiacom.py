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
        # self.headless = True
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
        # and if username used it will exctract Bearer Token
        # and use it for further login process
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
                self.browser.wait("//h2[normalize-space()='Your Profile']",
                                  By.XPATH, 10)
                self.browser.find("//h2[normalize-space()='Your Profile']",
                                  By.XPATH)
                storage = LocalStorage(self.browser._driver)
                if storage.has(self.localstorageuser):
                    self.bearer_token = '{token_type} {access_token}'.format(
                        **json.loads(storage[self.localstorageuser]))
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

        # Open chapters menu (note: the order of tabs in novel info
        # change whether if you are logged in or not)
        if len(self.browser.find_all('//*[starts-with(@id, "full-width-tab-")]',
                                     By.XPATH)) == 3:
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
            # wait until chapter fully loaded
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
    def __init__(self, driver):
        self.driver = driver

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def items(self):
        return self.driver.execute_script(
            "var ls = window.localStorage, items = {}; "
            "for (var i = 0, k; i < ls.length; ++i) "
            "  items[k = ls.key(i)] = ls.getItem(k); "
            "return items; "
        )

    def keys(self):
        return self.driver.execute_script(
            "var ls = window.localStorage, keys = []; "
            "for (var i = 0; i < ls.length; ++i) "
            "  keys[i] = ls.key(i); "
            "return keys; "
        )

    def get(self, key):
        return self.driver.execute_script(
            "return window.localStorage.getItem(arguments[0]);", key)

    def set(self, key, value):
        self.driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);",
            key, value)

    def has(self, key):
        return key in self.keys()

    def remove(self, key):
        self.driver.execute_script(
            "window.localStorage.removeItem(arguments[0]);", key)

    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")

    def __getitem__(self, key):
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


'''
DO NOT MODIFY THE FOLLOWING LINES UNLESS YOU KNOW WHAT YOU ARE DOING!
'''
WUXIWORLD_PROTO = json.loads('{"file": [{"name": "google/protobuf/wrappers.proto", "package": "google.protobuf", "messageType": [{"name": "DoubleValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_DOUBLE", "jsonName": "value"}]}, {"name": "FloatValue","field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_FLOAT", "jsonName": "value"}]}, {"name": "Int64Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT64", "jsonName": "value"}]}, {"name":"UInt64Value", "field": [{"name": "value", "number": 1, "label":"LABEL_OPTIONAL", "type": "TYPE_UINT64", "jsonName": "value"}]},{"name": "Int32Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "value"}]}, {"name": "UInt32Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_UINT32", "jsonName": "value"}]}, {"name": "BoolValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "value"}]}, {"name": "StringValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "value"}]}, {"name": "BytesValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BYTES", "jsonName": "value"}]}], "options": {"javaPackage":"com.google.protobuf", "javaOuterClassname": "WrappersProto", "javaMultipleFiles": true, "goPackage": "google.golang.org/protobuf/types/known/wrapperspb", "ccEnableArenas": true, "objcClassPrefix": "GPB", "csharpNamespace": "Google.Protobuf.WellKnownTypes"}, "syntax": "proto3"}, {"name": "google/protobuf/timestamp.proto", "package": "google.protobuf", "messageType": [{"name": "Timestamp", "field": [{"name": "seconds", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT64", "jsonName": "seconds"}, {"name": "nanos", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "nanos"}]}], "options": {"javaPackage": "com.google.protobuf", "javaOuterClassname": "TimestampProto", "javaMultipleFiles": true, "goPackage": "google.golang.org/protobuf/types/known/timestamppb", "ccEnableArenas": true, "objcClassPrefix": "GPB", "csharpNamespace": "Google.Protobuf.WellKnownTypes"}, "syntax": "proto3"}, {"name": "wuxia.proto", "package": "wuxiaworld.api.v2", "dependency": ["google/protobuf/wrappers.proto", "google/protobuf/timestamp.proto"], "messageType": [{"name": "RelatedChapterUserInfo", "field": [{"name": "isChapterUnlocked", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isChapterUnlocked"}, {"name": "isNovelUnlocked", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isNovelUnlocked"}, {"name": "isChapterFavorite", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isChapterFavorite"}, {"name": "isNovelOwned", "number": 4, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isNovelOwned"}, {"name": "isChapterOwned", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isChapterOwned"}]}, {"name": "ChapterSponsor", "field": [{"name": "advanceChapter", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "advanceChapter"}, {"name": "advanceChapterNumber","number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Int32Value", "jsonName": "advanceChapterNumber"}, {"name": "plans", "number": 3, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterSponsor.AdvanceChapterPlan", "jsonName": "plans"}], "nestedType": [{"name": "AdvanceChapterPlan", "field": [{"name": "name","number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "advanceChapterCount", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "advanceChapterCount"}]}]}, {"name": "ChapterPricing", "field": [{"name": "isFree", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isFree"}, {"name": "isLastHoldback", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isLastHoldback"}]}, {"name": "ChapterItem", "field": [{"name": "entityId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "entityId"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "slug", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "slug"}, {"name": "content", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "content"},{"name": "novelId", "number": 6, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}, {"name": "visible", "number": 7, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "visible"}, {"name": "isTeaser", "number": 8, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isTeaser"}, {"name": "spoilerTitle", "number": 10, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "spoilerTitle"}, {"name": "sponsorInfo", "number": 15, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterSponsor", "jsonName": "sponsorInfo"}, {"name": "relatedUserInfo", "number": 16, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.RelatedChapterUserInfo", "jsonName": "relatedUserInfo"}, {"name": "publishedAt", "number": 18, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Timestamp", "jsonName": "publishedAt"}, {"name": "translatorThoughts", "number": 19, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "translatorThoughts"}, {"name": "pricingInfo", "number": 20, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterPricing", "jsonName": "pricingInfo"}]}, {"name": "ChapterGroupItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "title", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "title"}, {"name": "order", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "order"}, {"name": "chapterList", "number": 6, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "chapterList"}]}, {"name": "SponsorPlanItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "enabled", "number": 4, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "enabled"}, {"name": "visible", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "visible"}, {"name": "advanceChapterCount", "number":6, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "advanceChapterCount"}, {"name": "paused", "number": 10, "label":"LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "paused"}]}, {"name": "NovelItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "coverUrl", "number": 10, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "coverUrl"}, {"name": "translatorName", "number": 11, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "translatorName"}, {"name": "authorName", "number": 13, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName":".google.protobuf.StringValue", "jsonName": "authorName"}, {"name": "isSneakPeek", "number": 18, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isSneakPeek"}]}, {"name": "UnlockedItem", "field": [{"name": "novelId", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "novelId"}, {"name": "chapterId", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "chapterId"}], "oneofDecl": [{"name": "id"}]}, {"name": "VipItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "enabled", "number": 7, "label": "LABEL_OPTIONAL","type": "TYPE_BOOL", "jsonName": "enabled"}, {"name": "visible","number": 8, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "visible"}]}, {"name": "SubscriptionItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "active", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "active"},{"name": "plan", "number": 3, "label": "LABEL_OPTIONAL", "type":"TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.SubscriptionItem.Plan", "jsonName": "plan"}], "nestedType": [{"name": "Plan", "field": [{"name": "vip", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.VipItem", "oneofIndex": 0, "jsonName": "vip"}, {"name": "sponsor", "number":2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.SponsorPlanItem", "oneofIndex": 0, "jsonName": "sponsor"}], "oneofDecl": [{"name": "plan"}]}]}, {"name": "GetChapterByProperty", "field": [{"name": "chapterId", "number": 1,"label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "chapterId"}, {"name": "slugs", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterByProperty.ByNovelAndChapterSlug", "oneofIndex": 0, "jsonName": "slugs"}], "nestedType": [{"name": "ByNovelAndChapterSlug", "field": [{"name": "novelSlug", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "novelSlug"}, {"name": "chapterSlug", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "chapterSlug"}]}], "oneofDecl": [{"name": "byProperty"}]}, {"name": "GetNovelRequest", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "id"}, {"name": "slug", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "oneofIndex": 0, "jsonName": "slug"}], "oneofDecl": [{"name": "selector"}]}, {"name": "GetNovelResponse", "field": [{"name":"item", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.NovelItem", "jsonName": "item"}]}, {"name": "GetChapterListRequest", "field": [{"name": "novelId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}, {"name": "filter", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterListRequest.FilterChapters", "jsonName":"filter"}], "nestedType": [{"name": "FilterChapters", "field": [{"name": "chapterGroupId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Int32Value", "jsonName": "chapterGroupId"}, {"name": "isAdvanceChapter", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isAdvanceChapter"}]}]}, {"name": "GetChapterListResponse", "field": [{"name":"items", "number": 1, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterGroupItem", "jsonName": "items"}, {"name": "novelInfo", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.NovelItem", "jsonName": "novelInfo"}]}, {"name": "GetChapterRequest", "field": [{"name": "chapterProperty", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterByProperty", "jsonName": "chapterProperty"}]}, {"name": "GetChapterResponse", "field": [{"name": "item", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "item"}]}, {"name": "UnlockItemRequest", "field": [{"name": "unlockMethod", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_ENUM", "typeName": ".wuxiaworld.api.v2.UnlockItemMethod", "jsonName": "unlockMethod"}, {"name": "item", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.UnlockedItem", "jsonName": "item"}]}, {"name": "UnlockItemResponse", "field": [{"name": "unlockedItem", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.UnlockedItem", "jsonName": "unlockedItem"}]}, {"name": "GetSubscriptionsRequest", "field": [{"name": "novelId", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}]}, {"name": "GetSubscriptionsResponse", "field": [{"name": "items", "number": 1, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.SubscriptionItem", "jsonName": "items"}]}], "enumType": [{"name": "UnlockItemMethod", "value": [{"name": "UnlockMethodNone", "number": 0}, {"name": "UnlockMethodKarma", "number": 1}, {"name": "UnlockMethodVip", "number": 2}, {"name": "UnlockMethodSponsor", "number": 3}]}], "service": [{"name": "Novels", "method": [{"name": "GetNovel", "inputType": ".wuxiaworld.api.v2.GetNovelRequest", "outputType": ".wuxiaworld.api.v2.GetNovelResponse"}]}, {"name": "Chapters", "method": [{"name": "GetChapterList", "inputType": ".wuxiaworld.api.v2.GetChapterListRequest", "outputType": ".wuxiaworld.api.v2.GetChapterListResponse"}, {"name": "GetChapter", "inputType": ".wuxiaworld.api.v2.GetChapterRequest", "outputType": ".wuxiaworld.api.v2.GetChapterResponse"}]}, {"name": "Unlocks", "method": [{"name": "UnlockItem", "inputType": ".wuxiaworld.api.v2.UnlockItemRequest", "outputType": ".wuxiaworld.api.v2.UnlockItemResponse"}]}, {"name": "Subscriptions", "method": [{"name": "GetSubscriptions", "inputType": ".wuxiaworld.api.v2.GetSubscriptionsRequest", "outputType": ".wuxiaworld.api.v2.GetSubscriptionsResponse"}]}], "publicDependency": [0, 1], "syntax": "proto3"}]}')  # noqa: E501
