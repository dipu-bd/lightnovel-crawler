# -*- coding: utf-8 -*-

import json
import logging
from collections import deque

from lncrawl.core import Chapter, LegacyCrawler

logger = logging.getLogger(__name__)


class NovelFrance(LegacyCrawler):
    base_url = ["https://novelfrance.fr"]
    has_manga = False
    has_mtl = False
    can_search = True

    api_path = "/api"  # Path of the API
    max_api_take = 100  # Max number of elements per API call
    download_chapter_with_api = True  # Use the API or BeautifulSoup to download

    # Call the API recursively, to get all the results in a path
    # path: the path, i.e. novelfrance.fr/api/<path>
    # other_params: (optional) dictionnary for the other params to encode in the URL, e.g.
    #   { q: "test" } -> ?q=test
    # returns a deque [ call_result, call_result, ...] with call_result containing JSON objects
    # one call can grab a maximum of <max_api_take> objects
    # so each call_result contains a maximum of <max_api_take> (100 by default)
    def api_call(self, path, other_params):
        result = deque([])
        # Transform our dictionary of params in URL Encoded params
        string_other_params = ""
        for param, value in other_params.items():
            string_other_params += "&" + param + "=" + value
        # First call to get the total number of results
        response = self.get_response(
            self.absolute_url(self.api_path) + "/" + path + "?take=1" + string_other_params
        ).text
        response_json = json.loads(response)
        has_more = response_json["hasMore"]  # If there is more results, this bool is True
        skip_number = 0  # First loop, don't skip any item
        if has_more:
            # The recursivity means the last element get added first, so appendleft to keep the order of the website
            result.appendleft(
                self.api_call_recursive(
                    path, self.max_api_take, skip_number, string_other_params, result
                )
            )
            return result
        # If there is nothing more (only one item!)
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
            # The recursivity means the last element get added first, so appendleft to keep the order of the website
            result.appendleft(
                self.api_call_recursive(
                    path, self.max_api_take, skip + self.max_api_take, string_other_params, result
                )
            )
        return response_json

    def search_novel(self, query):
        result = []
        query = query.lower().replace(" ", "+")  # Cleanup the query
        json_result = self.api_call("search", {"q": query})  # /api/search?q=
        for api_result in json_result:  # Deque of objects, each containing max 100 novels
            for novel in api_result["novels"]:
                result.append(
                    {
                        "title": novel["title"],
                        "url": self.absolute_url(self.api_path) + "/novels/" + novel["slug"],
                    }
                )
        return result

    def read_novel_info(self):
        # If the URL is not an API URL, tranform it into an API URL
        if "/api/" not in self.novel_url:
            # If HTTP, set to HTTPS
            self.novel_url = self.novel_url.replace("http://", "https://")
            # If www, remove it
            self.novel_url = self.novel_url.replace("https://www.", "https://")
            # Transform in API URL
            self.novel_url = self.novel_url.replace(
                self.absolute_url("/novel") + "/", self.absolute_url(self.api_path) + "/novels/"
            )

        # API call to /api/novels/<novel_name>/
        response = self.get_response(self.novel_url).text
        response_json = json.loads(response)

        # Synopsis
        self.novel_synopsis = response_json["description"]

        # Cover
        self.novel_cover = self.absolute_url(response_json["coverImage"])

        # Title
        self.novel_title = response_json["title"]

        # Tags
        self.novel_tags = []
        for tag in response_json["genres"]:
            self.novel_tags.append(tag["name"])

        # Author / translator
        self.novel_author = response_json["author"]
        if response_json["translatorName"]:
            self.novel_author += " | Translation : " + response_json["translatorName"]

        # Volumes
        # No volumes on this website, only chapters
        self.volumes.append(
            {
                "id": "1",
                "title": self.novel_title,
            }
        )

        # Chapters
        # API call to /api/chapters/<novel_name>/
        ## From the URL /api/novels/<novel_name>, remove /api/novels/
        novel_name = self.novel_url.replace(self.absolute_url(self.api_path) + "/novels/", "")
        ## From that, prefix with chapters/ to get chapters/<novel_name>
        path = "chapters/" + novel_name
        ## And work with absolute_url to get our URL
        url_chapters = self.absolute_url(self.api_path) + "/" + path
        json_result = self.api_call(path, {})
        for api_result in json_result:  # Deque of objects, each containing max 100 chapters...
            for chapter in api_result["chapters"]:
                self.chapters.append(
                    Chapter(
                        id=chapter["chapterNumber"],
                        volume="1",
                        url=url_chapters
                        + "/"
                        + chapter["slug"],  # /api/chapters/<novel_name>/<slug>
                        title=chapter["title"],
                    )
                )

    # Get chapter body
    # We can choose to download through API or BeautifulSoup
    # Through API, we have the raw text, no CSS or style
    # But it looks like extract_contents also remove all CSS/style
    # So... For now, we're using the API, but let's keep the other version just in case
    def download_chapter_body(self, chapter):
        # Download through API
        if self.download_chapter_with_api:
            ## The URL is already formed with the API! Just take the JSON
            response = self.get_response(chapter["url"]).text
            response_json = json.loads(response)
            ## The answers yield a list of paragraphs, so iterate through that
            list_paragraphs = []
            for paragraph in response_json["paragraphs"]:
                list_paragraphs.append(
                    "<p>" + paragraph["content"] + "</p>"
                )  # HTML format, <p>paragraph</p>
            return "".join(list_paragraphs)  # Returns a string with all paragraphs

        # or download through BeautifulSoup
        else:
            # Rework the URL
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
