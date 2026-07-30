# -*- coding: utf-8 -*-
import json
import logging
import re

from pyease_grpc import RpcSession
from requests.utils import CaseInsensitiveDict

from lncrawl.core import Chapter, Novel, SoupTemplate, Volume
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)


class WuxiaworldComCrawler(SoupTemplate):
    base_url = [
        "https://www.wuxiaworld.com/",
    ]

    def initialize(self):
        self.api_url = "https://api2.wuxiaworld.com"
        self.grpc = RpcSession.from_descriptor(WUXIWORLD_PROTO)
        self.grpc._session = self.scraper
        self.cleaner.bad_css.clear()
        self.cleaner.bad_tags.add("hr")
        self.bearer_token = None
        self.cleaner.unchanged_tags.update(["span"])

    def login(self, username_or_email: str, password_or_token: str) -> None:
        # Email and password went through the site's own login form in a browser, which
        # this source no longer drives. The token it used to extract can be supplied
        # directly: it is in local storage under the identity server's key.
        if username_or_email != "Bearer":
            raise LNException(
                "This source signs in with a token. "
                "Use 'Bearer' as the username and the access token as the password."
            )
        logger.info("login type: %s", username_or_email)
        self.bearer_token = username_or_email + " " + password_or_token

    def read_novel(self, novel: Novel) -> None:
        self.read_novel_in_soup(novel)

    def read_novel_in_soup(self, novel: Novel) -> None:
        slug = re.findall(r"/novel/([^/]+)", novel.url)[0]
        logger.info("Novel slug: %s", slug)

        headers = CaseInsensitiveDict(
            {
                "referer": novel.url,
                "origin": self.scraper.origin,
                "authorization": self.bearer_token,
            }
        )

        # Get novel details
        response = self.grpc.request(
            f"{self.api_url}/wuxiaworld.api.v2.Novels/GetNovel",
            {"slug": slug},
            headers=CaseInsensitiveDict(
                {
                    "referer": novel.url,
                    "origin": self.scraper.origin,
                    "authorization": self.bearer_token,
                }
            ),
        )

        if not response.single:
            raise LNException("No novel details in the API response")
        item = response.single["item"]

        novel.title = item["name"]
        novel.cover_url = item.get("coverUrl")
        novel.author = item.get("authorName")
        novel.synopsis = self.cleaner.extract_contents(item.get("synopsis"))

        # Get subscription details and whether advance chapter is allowed
        advance_chapter_allowed = 0
        try:
            response = self.grpc.request(
                f"{self.api_url}/wuxiaworld.api.v2.Subscriptions/GetSubscriptions",
                {"novelId": item["id"]},
                headers=headers,
            )

            if not response.single:
                raise LNException("No subscription details in the API response")
            subscriptions = response.single["items"]

            logger.debug(f"User subscriptions: {subscriptions}")
            for subscription in subscriptions:
                if "sponsor" in subscription["plan"]:
                    advance_chapter_allowed = subscription["plan"]["sponsor"]["advanceChapterCount"]
        except Exception as e:
            logger.debug(f"Failed to acquire subscription details. {e}")

        # Get table of contents
        novel.volumes = []
        novel.chapters = []

        response = self.grpc.request(
            f"{self.api_url}/wuxiaworld.api.v2.Chapters/GetChapterList",
            {"novelId": item["id"]},
            headers=headers,
        )

        if not response.single:
            raise LNException("No chapter list in the API response")
        volumes = response.single["items"]

        for group in sorted(volumes, key=lambda x: x.get("order", 0)):
            vol_id = len(novel.volumes) + 1
            novel.volumes.append(
                Volume(
                    id=vol_id,
                    title=group["title"],
                )
            )

            for chap in group["chapterList"]:
                chap_id = len(novel.chapters) + 1
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

                novel.chapters.append(
                    Chapter(
                        id=chap_id,
                        volume=vol_id,
                        title=chap_title,
                        original_title=chap["name"],
                        chapterId=chap["entityId"],
                        url=f"https://www.wuxiaworld.com/novel/{slug}/{chap['slug']}",
                    )
                )

        if not novel.chapters:
            raise LNException("No chapters found")

    def download_chapter(self, chapter: Chapter) -> None:
        self.download_chapter_in_soup(chapter)

    def download_chapter_in_soup(self, chapter: Chapter) -> None:
        response = self.grpc.request(
            f"{self.api_url}/wuxiaworld.api.v2.Chapters/GetChapter",
            {"chapterProperty": {"chapterId": chapter.chapterId}},
            headers=CaseInsensitiveDict(
                {
                    "referer": chapter.url,
                    "origin": self.scraper.origin,
                    "authorization": self.bearer_token,
                }
            ),
        )

        if not response.single:
            raise LNException("No chapter content in the API response")
        content = response.single["item"]["content"]

        if "translatorThoughts" in response.single["item"]:
            content += "<hr/>"
            content += "<blockquote><b>Translator's Thoughts</b>"
            content += response.single["item"]["translatorThoughts"]
            content += "</blockquote>"

        chapter.body = re.sub(r'(background-)?color: [^\\";]+', "", content)


"""
DO NOT MODIFY THE FOLLOWING LINES UNLESS YOU KNOW WHAT YOU ARE DOING
"""
WUXIWORLD_PROTO = json.loads(
    '{"file": [{"name": "google/protobuf/wrappers.proto", "package": "google.protobuf", "messageType": [{"name": "DoubleValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_DOUBLE", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "FloatValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_FLOAT", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "Int64Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT64", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "UInt64Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_UINT64", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "Int32Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "UInt32Value", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_UINT32", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "BoolValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "StringValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "BytesValue", "field": [{"name": "value", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BYTES", "jsonName": "value"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}], "options": {"javaPackage": "com.google.protobuf", "javaOuterClassname": "WrappersProto", "javaMultipleFiles": true, "goPackage": "google.golang.org/protobuf/types/known/wrapperspb", "ccEnableArenas": true, "objcClassPrefix": "GPB", "csharpNamespace": "Google.Protobuf.WellKnownTypes", "uninterpretedOption": []}, "syntax": "proto3", "dependency": [], "publicDependency": [], "weakDependency": [], "optionDependency": [], "enumType": [], "service": [], "extension": []}, {"name": "google/protobuf/timestamp.proto", "package": "google.protobuf", "messageType": [{"name": "Timestamp", "field": [{"name": "seconds", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT64", "jsonName": "seconds"}, {"name": "nanos", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "nanos"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}], "options": {"javaPackage": "com.google.protobuf", "javaOuterClassname": "TimestampProto", "javaMultipleFiles": true, "goPackage": "google.golang.org/protobuf/types/known/timestamppb", "ccEnableArenas": true, "objcClassPrefix": "GPB", "csharpNamespace": "Google.Protobuf.WellKnownTypes", "uninterpretedOption": []}, "syntax": "proto3", "dependency": [], "publicDependency": [], "weakDependency": [], "optionDependency": [], "enumType": [], "service": [], "extension": []}, {"name": "wuxia.proto", "package": "wuxiaworld.api.v2", "dependency": ["google/protobuf/wrappers.proto", "google/protobuf/timestamp.proto"], "messageType": [{"name": "RelatedChapterUserInfo", "field": [{"name": "isChapterUnlocked", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isChapterUnlocked"}, {"name": "isNovelUnlocked", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isNovelUnlocked"}, {"name": "isChapterFavorite", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isChapterFavorite"}, {"name": "isNovelOwned", "number": 4, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isNovelOwned"}, {"name": "isChapterOwned", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isChapterOwned"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "ChapterSponsor", "field": [{"name": "advanceChapter", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "advanceChapter"}, {"name": "advanceChapterNumber", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Int32Value", "jsonName": "advanceChapterNumber"}, {"name": "plans", "number": 3, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterSponsor.AdvanceChapterPlan", "jsonName": "plans"}], "nestedType": [{"name": "AdvanceChapterPlan", "field": [{"name": "name", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "advanceChapterCount", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "advanceChapterCount"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}], "extension": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "ChapterPricing", "field": [{"name": "isFree", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isFree"}, {"name": "isLastHoldback", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isLastHoldback"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "ChapterItem", "field": [{"name": "entityId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "entityId"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "slug", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "slug"}, {"name": "content", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "content"}, {"name": "novelId", "number": 6, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}, {"name": "visible", "number": 7, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "visible"}, {"name": "isTeaser", "number": 8, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isTeaser"}, {"name": "spoilerTitle", "number": 10, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "spoilerTitle"}, {"name": "sponsorInfo", "number": 15, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterSponsor", "jsonName": "sponsorInfo"}, {"name": "relatedUserInfo", "number": 16, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.RelatedChapterUserInfo", "jsonName": "relatedUserInfo"}, {"name": "publishedAt", "number": 18, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Timestamp", "jsonName": "publishedAt"}, {"name": "translatorThoughts", "number": 19, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "translatorThoughts"}, {"name": "pricingInfo", "number": 20, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterPricing", "jsonName": "pricingInfo"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "ChapterGroupItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "title", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "title"}, {"name": "order", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "order"}, {"name": "chapterList", "number": 6, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "chapterList"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "SponsorPlanItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "enabled", "number": 4, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "enabled"}, {"name": "visible", "number": 5, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "visible"}, {"name": "advanceChapterCount", "number": 6, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "advanceChapterCount"}, {"name": "paused", "number": 10, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "paused"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "NovelItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "synopsis", "number": 9, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "synopsis"}, {"name": "coverUrl", "number": 10, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "coverUrl"}, {"name": "translatorName", "number": 11, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "translatorName"}, {"name": "authorName", "number": 13, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.StringValue", "jsonName": "authorName"}, {"name": "isSneakPeek", "number": 18, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "isSneakPeek"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "UnlockedItem", "field": [{"name": "novelId", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "novelId"}, {"name": "chapterId", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "chapterId"}], "oneofDecl": [{"name": "id"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "reservedRange": [], "reservedName": []}, {"name": "VipItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "name", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "name"}, {"name": "enabled", "number": 7, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "enabled"}, {"name": "visible", "number": 8, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "visible"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "SubscriptionItem", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "id"}, {"name": "active", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_BOOL", "jsonName": "active"}, {"name": "plan", "number": 3, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.SubscriptionItem.Plan", "jsonName": "plan"}], "nestedType": [{"name": "Plan", "field": [{"name": "vip", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.VipItem", "oneofIndex": 0, "jsonName": "vip"}, {"name": "sponsor", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.SponsorPlanItem", "oneofIndex": 0, "jsonName": "sponsor"}], "oneofDecl": [{"name": "plan"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "reservedRange": [], "reservedName": []}], "extension": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "GetChapterByProperty", "field": [{"name": "chapterId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "chapterId"}, {"name": "slugs", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterByProperty.ByNovelAndChapterSlug", "oneofIndex": 0, "jsonName": "slugs"}], "nestedType": [{"name": "ByNovelAndChapterSlug", "field": [{"name": "novelSlug", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "novelSlug"}, {"name": "chapterSlug", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "jsonName": "chapterSlug"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}], "oneofDecl": [{"name": "byProperty"}], "extension": [], "enumType": [], "extensionRange": [], "reservedRange": [], "reservedName": []}, {"name": "GetNovelRequest", "field": [{"name": "id", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "oneofIndex": 0, "jsonName": "id"}, {"name": "slug", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_STRING", "oneofIndex": 0, "jsonName": "slug"}], "oneofDecl": [{"name": "selector"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "reservedRange": [], "reservedName": []}, {"name": "GetNovelResponse", "field": [{"name": "item", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.NovelItem", "jsonName": "item"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "GetChapterListRequest", "field": [{"name": "novelId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}, {"name": "filter", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterListRequest.FilterChapters", "jsonName": "filter"}], "nestedType": [{"name": "FilterChapters", "field": [{"name": "chapterGroupId", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.Int32Value", "jsonName": "chapterGroupId"}, {"name": "isAdvanceChapter", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".google.protobuf.BoolValue", "jsonName": "isAdvanceChapter"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}], "extension": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "GetChapterListResponse", "field": [{"name": "items", "number": 1, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterGroupItem", "jsonName": "items"}, {"name": "novelInfo", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.NovelItem", "jsonName": "novelInfo"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "GetChapterRequest", "field": [{"name": "chapterProperty", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.GetChapterByProperty", "jsonName": "chapterProperty"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "GetChapterResponse", "field": [{"name": "item", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.ChapterItem", "jsonName": "item"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "UnlockItemRequest", "field": [{"name": "unlockMethod", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_ENUM", "typeName": ".wuxiaworld.api.v2.UnlockItemMethod", "jsonName": "unlockMethod"}, {"name": "item", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.UnlockedItem", "jsonName": "item"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "UnlockItemResponse", "field": [{"name": "unlockedItem", "number": 1, "label": "LABEL_OPTIONAL", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.UnlockedItem", "jsonName": "unlockedItem"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "GetSubscriptionsRequest", "field": [{"name": "novelId", "number": 2, "label": "LABEL_OPTIONAL", "type": "TYPE_INT32", "jsonName": "novelId"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}, {"name": "GetSubscriptionsResponse", "field": [{"name": "items", "number": 1, "label": "LABEL_REPEATED", "type": "TYPE_MESSAGE", "typeName": ".wuxiaworld.api.v2.SubscriptionItem", "jsonName": "items"}], "extension": [], "nestedType": [], "enumType": [], "extensionRange": [], "oneofDecl": [], "reservedRange": [], "reservedName": []}], "enumType": [{"name": "UnlockItemMethod", "value": [{"name": "UnlockMethodNone", "number": 0}, {"name": "UnlockMethodKarma", "number": 1}, {"name": "UnlockMethodVip", "number": 2}, {"name": "UnlockMethodSponsor", "number": 3}], "reservedRange": [], "reservedName": []}], "service": [{"name": "Novels", "method": [{"name": "GetNovel", "inputType": ".wuxiaworld.api.v2.GetNovelRequest", "outputType": ".wuxiaworld.api.v2.GetNovelResponse"}]}, {"name": "Chapters", "method": [{"name": "GetChapterList", "inputType": ".wuxiaworld.api.v2.GetChapterListRequest", "outputType": ".wuxiaworld.api.v2.GetChapterListResponse"}, {"name": "GetChapter", "inputType": ".wuxiaworld.api.v2.GetChapterRequest", "outputType": ".wuxiaworld.api.v2.GetChapterResponse"}]}, {"name": "Unlocks", "method": [{"name": "UnlockItem", "inputType": ".wuxiaworld.api.v2.UnlockItemRequest", "outputType": ".wuxiaworld.api.v2.UnlockItemResponse"}]}, {"name": "Subscriptions", "method": [{"name": "GetSubscriptions", "inputType": ".wuxiaworld.api.v2.GetSubscriptionsRequest", "outputType": ".wuxiaworld.api.v2.GetSubscriptionsResponse"}]}], "publicDependency": [0, 1], "syntax": "proto3", "weakDependency": [], "optionDependency": [], "extension": []}]}'
)
