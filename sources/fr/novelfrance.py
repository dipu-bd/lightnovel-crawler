# -*- coding: utf-8 -*-

from collections import deque
import json
import logging

from lncrawl.core import Chapter, LegacyCrawler

logger = logging.getLogger(__name__)


class NovelFrance(LegacyCrawler):
    base_url = ["https://novelfrance.fr"]
    has_manga = False
    has_mtl = False
    can_search = True

    api_path = "/api"
    max_api_take = 100
    download_chapter_with_api = True

    def api_call(self, path, other_params):
        result = deque([])
        string_other_params = ""
        for param, value in other_params.items():
            string_other_params += "&" + param + "=" + value
        response = self.get_response(
            self.absolute_url(self.api_path) + "/" + path + "?take=1" + string_other_params
        ).text
        response_json = json.loads(response)
        has_more = response_json["hasMore"]
        skip_number = 0
        if has_more:
            result.appendleft(
                self.api_call_recursive(
                    path, self.max_api_take, skip_number, string_other_params, result
                )
            )
            return result
        result.appendleft(response_json)
        return result

    def api_call_recursive(self, path, take, skip, string_other_params, result):
        response = self.get_response(
            self.absolute_url(self.api_path)
            + "/"
            + path
            + "?take="
            + str(take)
            + "&skip="
            + str(skip)
            + "&order=asc"
            + string_other_params
        ).text
        response_json = json.loads(response)
        has_more = response_json["hasMore"]
        if has_more:
            result.appendleft(
                self.api_call_recursive(
                    path, self.max_api_take, skip + self.max_api_take, string_other_params, result
                )
            )
        return response_json

    def search_novel(self, query):
        result = []
        query = query.lower().replace(" ", "+")
        json_result = self.api_call("search", {"q": query})
        for api_result in json_result:
            for novel in api_result["novels"]:
                result.append(
                    {
                        "title": novel["title"],
                        "url": self.absolute_url(self.api_path) + "/novels/" + novel["slug"],
                    }
                )
        return result

    def read_novel_info(self):
        if "/api/" not in self.novel_url:
            self.novel_url = self.novel_url.replace("http://", "https://")
            self.novel_url = self.novel_url.replace("https://www.", "https://")
            self.novel_url = self.novel_url.replace(
                self.absolute_url("/novel") + "/", self.absolute_url(self.api_path) + "/novels/"
            )
        response = self.get_response(self.novel_url).text
        response_json = json.loads(response)
        self.novel_synopsis = response_json["description"]
        self.novel_cover = self.absolute_url(response_json["coverImage"])
        self.novel_title = response_json["title"]
        self.novel_tags = []
        for tag in response_json["genres"]:
            self.novel_tags.append(tag["name"])
        self.novel_author = response_json["author"]
        if response_json["translatorName"]:
            self.novel_author += " | Translation : " + response_json["translatorName"]
        self.volumes.append(
            {
                "id": "1",
                "title": self.novel_title,
            }
        )
        novel_name = self.novel_url.replace(self.absolute_url(self.api_path) + "/novels/", "")
        path = "chapters/" + novel_name
        url_chapters = self.absolute_url(self.api_path) + "/" + path
        json_result = self.api_call(path, {})
        for api_result in json_result:
            for chapter in api_result["chapters"]:
                self.chapters.append(
                    Chapter(
                        id=chapter["chapterNumber"],
                        volume="1",
                        url=url_chapters + "/" + chapter["slug"],
                        title=chapter["title"],
                    )
                )

    def download_chapter_body(self, chapter):
        if self.download_chapter_with_api:
            response = self.get_response(chapter["url"]).text
            response_json = json.loads(response)
            list_paragraphs = []
            for paragraph in response_json["paragraphs"]:
                list_paragraphs.append("<p>" + paragraph["content"] + "</p>")
            return "".join(list_paragraphs)
        else:
            url_browser = chapter["url"].replace(
                self.absolute_url(self.api_path) + "/chapters/", self.absolute_url("/novel") + "/"
            )
            soup = self.get_soup(url_browser)
            content = soup.find(
                "div",
                {
                    "class": "chapter-content",
                },
            )
            return self.cleaner.extract_contents(content)
