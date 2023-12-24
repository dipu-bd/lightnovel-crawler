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
        self.localstorageuser = 'oidc.user:' \
                                'https://identity.wuxiaworld.com' \
                                ':wuxiaworld_spa'

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
                f"{self.api_url}" +
                "/wuxiaworld.api.v2.Subscriptions/GetSubscriptions",
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
                        url="https://www.wuxiaworld.com/novel" +
                        f"/{slug}/{chap['slug']}",
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
        self.browser.wait(".items-start h1, " +
                          "img.drop-shadow-ww-novel-cover-image")

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
        if len(self.browser.find_all('//*[starts-with' +
                                     '(@id, "full-width-tab-")]',
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
            self.browser.wait("#app .MuiAccordion-root:" +
                              f"nth-of-type({nth}) a[href]")

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
                        self.browser.wait("//h2[normalize-space()" +
                                          "='Your Profile']", By.XPATH, 10)
                        self.browser.find("//h2[normalize-space()" +
                                          "='Your Profile']", By.XPATH)
                    except Exception as e:
                        logger.debug("login Email: Failed", e)
            self.start_download_chapter_body_in_browser = True
        self.visit(chapter.url)
        try:
            # wait untill chapter fully loaded
            self.browser.wait("chapter-content", By.CLASS_NAME)
            if self.bearer_token:
                self.browser.wait("//button[normalize-space()" +
                                  "='Favorite']", By.XPATH, 10)
                self.browser.find("//button[normalize-space()" +
                                  "='Favorite']", By.XPATH)
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


WUXIWORLD_PROTO = json.loads(
    '{"file": [{"name": "google/protobuf/wrappers.proto", "package": "\
google.protobuf", "messageType": [{"name": "DoubleValue", "field"\
: [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "typ\
e": "TYPE_DOUBLE", "jsonName": "value"}]}, {"name": "FloatValue",\
 "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONA\
L", "type": "TYPE_FLOAT", "jsonName": "value"}]}, {"name": "Int64\
Value", "field": [{"name": "value", "number": 1, "label": "LABEL_\
OPTIONAL", "type": "TYPE_INT64", "jsonName": "value"}]}, {"name":\
 "UInt64Value", "field": [{"name": "value", "number": 1, "label":\
 "LABEL_OPTIONAL", "type": "TYPE_UINT64", "jsonName": "value"}]},\
 {"name": "Int32Value", "field": [{"name": "value", "number": 1, \
"label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "val\
ue"}]}, {"name": "UInt32Value", "field": [{"name": "value", "numb\
er": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_UINT32", "jsonNa\
me": "value"}]}, {"name": "BoolValue", "field": [{"name": "value"\
, "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "j\
sonName": "value"}]}, {"name": "StringValue", "field": [{"name": \
"value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_ST\
RING", "jsonName": "value"}]}, {"name": "BytesValue", "field": [{\
"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": \
"TYPE_BYTES", "jsonName": "value"}]}], "options": {"javaPackage":\
 "com.google.protobuf", "javaOuterClassname": "WrappersProto", "j\
avaMultipleFiles": true, "goPackage": "google.golang.org/protobuf\
/types/known/wrapperspb", "ccEnableArenas": true, "objcClassPrefi\
x": "GPB", "csharpNamespace": "Google.Protobuf.WellKnownTypes"}, \
"syntax": "proto3"}, {"name": "google/protobuf/timestamp.proto", \
"package": "google.protobuf", "messageType": [{"name": "Timestamp\
", "field": [{"name": "seconds", "number": 1, "label": "LABEL_OPT\
IONAL", "type": "TYPE_INT64", "jsonName": "seconds"}, {"name": "n\
anos", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT3\
2", "jsonName": "nanos"}]}], "options": {"javaPackage": "com.goog\
le.protobuf", "javaOuterClassname": "TimestampProto", "javaMultip\
leFiles": true, "goPackage": "google.golang.org/protobuf/types/kn\
own/timestamppb", "ccEnableArenas": true, "objcClassPrefix": "GPB\
", "csharpNamespace": "Google.Protobuf.WellKnownTypes"}, "syntax"\
: "proto3"}, {"name": "wuxia.proto", "package": "wuxiaworld.api.v\
2", "dependency": ["google/protobuf/wrappers.proto", "google/prot\
obuf/timestamp.proto"], "messageType": [{"name": "RelatedChapterU\
serInfo", "field": [{"name": "isChapterUnlocked", "number": 1, "l\
abel": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".go\
ogle.protobuf.BoolValue", "jsonName": "isChapterUnlocked"}, {"nam\
e": "isNovelUnlocked", "number": 2, "label": "LABEL_OPTIONAL", "t\
ype": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "\
jsonName": "isNovelUnlocked"}, {"name": "isChapterFavorite", "num\
ber": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "type\
Name": ".google.protobuf.BoolValue", "jsonName": "isChapterFavori\
te"}, {"name": "isNovelOwned", "number": 4, "label": "LABEL_OPTIO\
NAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolV\
alue", "jsonName": "isNovelOwned"}, {"name": "isChapterOwned", "n\
umber": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "ty\
peName": ".google.protobuf.BoolValue", "jsonName": "isChapterOwne\
d"}]}, {"name": "ChapterSponsor", "field": [{"name": "advanceChap\
ter", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL"\
, "jsonName": "advanceChapter"}, {"name": "advanceChapterNumber",\
 "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", \
"typeName": ".google.protobuf.Int32Value", "jsonName": "advanceCh\
apterNumber"}, {"name": "plans", "number": 3, "label": "LABEL_REP\
EATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.C\
hapterSponsor.AdvanceChapterPlan", "jsonName": "plans"}], "nested\
Type": [{"name": "AdvanceChapterPlan", "field": [{"name": "name",\
 "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "\
jsonName": "name"}, {"name": "advanceChapterCount", "number": 2, \
"label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "adv\
anceChapterCount"}]}]}, {"name": "ChapterPricing", "field": [{"na\
me": "isFree", "number": 1, "label": "LABEL_OPTIONAL", "type": "T\
YPE_BOOL", "jsonName": "isFree"}, {"name": "isLastHoldback", "num\
ber": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonNam\
e": "isLastHoldback"}]}, {"name": "ChapterItem", "field": [{"name\
": "entityId", "number": 1, "label": "LABEL_OPTIONAL", "type": "T\
YPE_INT32", "jsonName": "entityId"}, {"name": "name", "number": 2\
, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "\
name"}, {"name": "slug", "number": 3, "label": "LABEL_OPTIONAL", \
"type": "TYPE_STRING", "jsonName": "slug"}, {"name": "content", "\
number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "t\
ypeName": ".google.protobuf.StringValue", "jsonName": "content"},\
 {"name": "novelId", "number": 6, "label": "LABEL_OPTIONAL", "typ\
e": "TYPE_INT32", "jsonName": "novelId"}, {"name": "visible", "nu\
mber": 7, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonNa\
me": "visible"}, {"name": "isTeaser", "number": 8, "label": "LABE\
L_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isTeaser"}, {"name\
": "spoilerTitle", "number": 10, "label": "LABEL_OPTIONAL", "type\
": "TYPE_BOOL", "jsonName": "spoilerTitle"}, {"name": "sponsorInf\
o", "number": 15, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAG\
E", "typeName": ".wuxiaworld.api.v2.ChapterSponsor", "jsonName": \
"sponsorInfo"}, {"name": "relatedUserInfo", "number": 16, "label"\
: "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiawo\
rld.api.v2.RelatedChapterUserInfo", "jsonName": "relatedUserInfo"\
}, {"name": "publishedAt", "number": 18, "label": "LABEL_OPTIONAL\
", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Timestam\
p", "jsonName": "publishedAt"}, {"name": "translatorThoughts", "n\
umber": 19, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "t\
ypeName": ".google.protobuf.StringValue", "jsonName": "translator\
Thoughts"}, {"name": "pricingInfo", "number": 20, "label": "LABEL\
_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.\
v2.ChapterPricing", "jsonName": "pricingInfo"}]}, {"name": "Chapt\
erGroupItem", "field": [{"name": "id", "number": 1, "label": "LAB\
EL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "\
title", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STR\
ING", "jsonName": "title"}, {"name": "order", "number": 3, "label\
": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "order"}, \
{"name": "chapterList", "number": 6, "label": "LABEL_REPEATED", "\
type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterIte\
m", "jsonName": "chapterList"}]}, {"name": "SponsorPlanItem", "fi\
eld": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "ty\
pe": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": \
2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": \
"name"}, {"name": "enabled", "number": 4, "label": "LABEL_OPTIONA\
L", "type": "TYPE_BOOL", "jsonName": "enabled"}, {"name": "visibl\
e", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", \
"jsonName": "visible"}, {"name": "advanceChapterCount", "number":\
 6, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": \
"advanceChapterCount"}, {"name": "paused", "number": 10, "label":\
 "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "paused"}]}, \
{"name": "NovelItem", "field": [{"name": "id", "number": 1, "labe\
l": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"\
name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "T\
YPE_STRING", "jsonName": "name"}, {"name": "coverUrl", "number": \
10, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName"\
: ".google.protobuf.StringValue", "jsonName": "coverUrl"}, {"name\
": "translatorName", "number": 11, "label": "LABEL_OPTIONAL", "ty\
pe": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", \
"jsonName": "translatorName"}, {"name": "authorName", "number": 1\
3, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName":\
 ".google.protobuf.StringValue", "jsonName": "authorName"}, {"nam\
e": "isSneakPeek", "number": 18, "label": "LABEL_OPTIONAL", "type\
": "TYPE_BOOL", "jsonName": "isSneakPeek"}]}, {"name": "UnlockedI\
tem", "field": [{"name": "novelId", "number": 2, "label": "LABEL_\
OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "no\
velId"}, {"name": "chapterId", "number": 3, "label": "LABEL_OPTIO\
NAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "chapter\
Id"}], "oneofDecl": [{"name": "id"}]}, {"name": "VipItem", "field\
": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type"\
: "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, \
"label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "na\
me"}, {"name": "enabled", "number": 7, "label": "LABEL_OPTIONAL",\
 "type": "TYPE_BOOL", "jsonName": "enabled"}, {"name": "visible",\
 "number": 8, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "js\
onName": "visible"}]}, {"name": "SubscriptionItem", "field": [{"n\
ame": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE\
_INT32", "jsonName": "id"}, {"name": "active", "number": 2, "labe\
l": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "active"},\
 {"name": "plan", "number": 3, "label": "LABEL_OPTIONAL", "type":\
 "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.SubscriptionItem\
.Plan", "jsonName": "plan"}], "nestedType": [{"name": "Plan", "fi\
eld": [{"name": "vip", "number": 1, "label": "LABEL_OPTIONAL", "t\
ype": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.VipItem", "\
oneofIndex": 0, "jsonName": "vip"}, {"name": "sponsor", "number":\
 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName"\
: ".wuxiaworld.api.v2.SponsorPlanItem", "oneofIndex": 0, "jsonNam\
e": "sponsor"}], "oneofDecl": [{"name": "plan"}]}]}, {"name": "Ge\
tChapterByProperty", "field": [{"name": "chapterId", "number": 1,\
 "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0\
, "jsonName": "chapterId"}, {"name": "slugs", "number": 2, "label\
": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaw\
orld.api.v2.GetChapterByProperty.ByNovelAndChapterSlug", "oneofIn\
dex": 0, "jsonName": "slugs"}], "nestedType": [{"name": "ByNovelA\
ndChapterSlug", "field": [{"name": "novelSlug", "number": 1, "lab\
el": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "novelS\
lug"}, {"name": "chapterSlug", "number": 2, "label": "LABEL_OPTIO\
NAL", "type": "TYPE_STRING", "jsonName": "chapterSlug"}]}], "oneo\
fDecl": [{"name": "byProperty"}]}, {"name": "GetNovelRequest", "f\
ield": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "t\
ype": "TYPE_INT32", "oneofIndex": 0, "jsonName": "id"}, {"name": \
"slug", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STR\
ING", "oneofIndex": 0, "jsonName": "slug"}], "oneofDecl": [{"name\
": "selector"}]}, {"name": "GetNovelResponse", "field": [{"name":\
 "item", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_ME\
SSAGE", "typeName": ".wuxiaworld.api.v2.NovelItem", "jsonName": "\
item"}]}, {"name": "GetChapterListRequest", "field": [{"name": "n\
ovelId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_IN\
T32", "jsonName": "novelId"}, {"name": "filter", "number": 2, "la\
bel": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wux\
iaworld.api.v2.GetChapterListRequest.FilterChapters", "jsonName":\
 "filter"}], "nestedType": [{"name": "FilterChapters", "field": [\
{"name": "chapterGroupId", "number": 1, "label": "LABEL_OPTIONAL"\
, "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Int32Valu\
e", "jsonName": "chapterGroupId"}, {"name": "isAdvanceChapter", "\
number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "t\
ypeName": ".google.protobuf.BoolValue", "jsonName": "isAdvanceCha\
pter"}]}]}, {"name": "GetChapterListResponse", "field": [{"name":\
 "items", "number": 1, "label": "LABEL_REPEATED", "type": "TYPE_M\
ESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterGroupItem", "json\
Name": "items"}, {"name": "novelInfo", "number": 2, "label": "LAB\
EL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.ap\
i.v2.NovelItem", "jsonName": "novelInfo"}]}, {"name": "GetChapter\
Request", "field": [{"name": "chapterProperty", "number": 1, "lab\
el": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxi\
aworld.api.v2.GetChapterByProperty", "jsonName": "chapterProperty\
"}]}, {"name": "GetChapterResponse", "field": [{"name": "item", "\
number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "t\
ypeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "item"}]}\
, {"name": "UnlockItemRequest", "field": [{"name": "unlockMethod"\
, "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_ENUM", "t\
ypeName": ".wuxiaworld.api.v2.UnlockItemMethod", "jsonName": "unl\
ockMethod"}, {"name": "item", "number": 2, "label": "LABEL_OPTION\
AL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.Unlo\
ckedItem", "jsonName": "item"}]}, {"name": "UnlockItemResponse", \
"field": [{"name": "unlockedItem", "number": 1, "label": "LABEL_O\
PTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2\
.UnlockedItem", "jsonName": "unlockedItem"}]}, {"name": "GetSubsc\
riptionsRequest", "field": [{"name": "novelId", "number": 2, "lab\
el": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId\
"}]}, {"name": "GetSubscriptionsResponse", "field": [{"name": "it\
ems", "number": 1, "label": "LABEL_REPEATED", "type": "TYPE_MESSA\
GE", "typeName": ".wuxiaworld.api.v2.SubscriptionItem", "jsonName\
": "items"}]}], "enumType": [{"name": "UnlockItemMethod", "value"\
: [{"name": "UnlockMethodNone", "number": 0}, {"name": "UnlockMet\
hodKarma", "number": 1}, {"name": "UnlockMethodVip", "number": 2}\
, {"name": "UnlockMethodSponsor", "number": 3}]}], "service": [{"\
name": "Novels", "method": [{"name": "GetNovel", "inputType": ".w\
uxiaworld.api.v2.GetNovelRequest", "outputType": ".wuxiaworld.api\
.v2.GetNovelResponse"}]}, {"name": "Chapters", "method": [{"name"\
: "GetChapterList", "inputType": ".wuxiaworld.api.v2.GetChapterLi\
stRequest", "outputType": ".wuxiaworld.api.v2.GetChapterListRespo\
nse"}, {"name": "GetChapter", "inputType": ".wuxiaworld.api.v2.Ge\
tChapterRequest", "outputType": ".wuxiaworld.api.v2.GetChapterRes\
ponse"}]}, {"name": "Unlocks", "method": [{"name": "UnlockItem", \
"inputType": ".wuxiaworld.api.v2.UnlockItemRequest", "outputType"\
: ".wuxiaworld.api.v2.UnlockItemResponse"}]}, {"name": "Subscript\
ions", "method": [{"name": "GetSubscriptions", "inputType": ".wux\
iaworld.api.v2.GetSubscriptionsRequest", "outputType": ".wuxiawor\
ld.api.v2.GetSubscriptionsResponse"}]}], "publicDependency": [0, \
1], "syntax": "proto3"}]}')  # noqa: E501
