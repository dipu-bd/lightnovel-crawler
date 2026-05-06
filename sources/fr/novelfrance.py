# -*- coding: utf-8 -*-

import json
import logging
from collections import deque

from lncrawl.core import Chapter, LegacyCrawler

logger = logging.getLogger(__name__)


# We have a lovely API for this one, so let's use it! To the devs at NovelFrance, thank you! <3
class NovelFrance(LegacyCrawler):
    base_url = ["https://novelfrance.fr"]
    has_manga = False
    has_mtl = False
    can_search = True  # Not sure if needed

    apiPath = "/api"  # Path of the API
    maxApiTake = 100  # Max number of elements per API call
    downloadChapterWithApi = True  # Use the API or BeautifulSoup to download

    # Call the API recursively, to get all the results in a path
    # path: the path, i.e. novelfrance.fr/api/<path>
    # otherParams: (optional) dictionnary for the other params to encode in the URL, e.g.
    #   { q: "test" } -> ?q=test
    # returns a deque [ callResult, callResult, ...] with callResult containing JSON objects
    # one call can grab a maximum of <maxApiTake> objects
    # so each callResult contains a maximum of <maxApiTake> (100 by default)
    def apiCall(self, path, otherParams):
        # Init the resulting deque
        result = deque([])
        # Transform our dictionary of params in URL Encoded params
        stringOtherParams = ""
        for param, value in otherParams.items():
            stringOtherParams += "&" + param + "=" + value
        # First call to get the total number of results
        response = self.get_response(
            self.absolute_url(self.apiPath) + "/" + path + "?take=1" + stringOtherParams
        ).text
        responseJson = json.loads(response)
        hasMore = responseJson["hasMore"]  # If there is more results, this bool is True
        skipNumber = 0  # First loop, don't skip any item
        if hasMore:
            # the recursivity means the last element get added first, so appendleft to keep the order of the website
            result.appendleft(
                self.apiCallRecursive(path, self.maxApiTake, skipNumber, stringOtherParams, result)
            )
            return result
        # If there is nothing more (only one item!)
        result.appendleft(responseJson)
        return result

    def apiCallRecursive(self, path, take, skip, stringOtherParams, result):
        # Call the API
        response = self.get_response(
            self.absolute_url(self.apiPath)
            + "/"
            + path
            + "?take="
            + str(take)
            + "&skip="
            + str(skip)
            + "&order=asc"
            + stringOtherParams
        ).text
        responseJson = json.loads(response)
        hasMore = responseJson["hasMore"]  # Is there more results?
        if hasMore:
            # the recursivity means the last element get added first, so appendleft to keep the order of the website
            result.appendleft(
                self.apiCallRecursive(
                    path, self.maxApiTake, skip + self.maxApiTake, stringOtherParams, result
                )
            )
        return responseJson

    def search_novel(self, query):
        result = []
        query = query.lower().replace(" ", "+")  # Cleanup the query
        jsonResult = self.apiCall("search", {"q": query})  # /api/search?q=
        for apiResult in jsonResult:  # Deque of objects, each containing max 100 novels...
            for novel in apiResult["novels"]:  # For each novel in this object
                result.append(
                    {
                        "title": novel["title"],
                        "url": self.absolute_url(self.apiPath) + "/novels/" + novel["slug"],
                    }
                )
        return result

    def read_novel_info(self):
        # If the URL is not an API URL, tranform it into an API URL
        if "/api/" not in self.novel_url:
            # If HTTP (!!!), set to HTTPS
            self.novel_url = self.novel_url.replace("http://", "https://")
            # If www, remove it
            self.novel_url = self.novel_url.replace("https://www.", "https://")
            # Transform in API URL
            self.novel_url = self.novel_url.replace(
                self.absolute_url("/novel") + "/", self.absolute_url(self.apiPath) + "/novels/"
            )

        # API call to /api/novels/<novel_name>/
        response = self.get_response(self.novel_url).text  # Call the API to get the novel
        responseJson = json.loads(response)  # Get JSON

        # Synopsis
        self.novel_synopsis = responseJson["description"]

        # Cover
        self.novel_cover = self.absolute_url(responseJson["coverImage"])

        # Title
        self.novel_title = responseJson["title"]

        # Tags
        self.novel_tags = []
        for tag in responseJson["genres"]:
            self.novel_tags.append(tag["name"])

        # Author / translator
        self.novel_author = responseJson["author"]
        if responseJson["translatorName"]:
            self.novel_author += " | Traduction : " + responseJson["translatorName"]

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
        ## From the URL /api/novels/<novel_name>, remove the whole /api/novels/
        novelName = self.novel_url.replace(self.absolute_url(self.apiPath) + "/novels/", "")
        ## From that, prefix with chapters/ to get chapters/<novel_name>
        path = "chapters/" + novelName
        ## And work with absolute_url to have our URL!
        urlChapters = self.absolute_url(self.apiPath) + "/" + path
        jsonResult = self.apiCall(path, {})
        for apiResult in jsonResult:  # Deque of objects, each containing max 100 chapters...
            for chapter in apiResult["chapters"]:  # Go through all chapters in this object
                self.chapters.append(
                    Chapter(
                        id=chapter["chapterNumber"],
                        volume="1",
                        url=urlChapters
                        + "/"
                        + chapter["slug"],  # /api/chapters/<novel_name>/<slug>
                        title=chapter["title"],
                    )
                )

    # Get chapter body
    # We can choose to download through API or BeautifulSoup
    # Through API, we have the raw text, no CSS or style
    # But it looks like the extract_contents also remove all CSS/style
    # So... For now, we're using the API, but let's keep the other version just in case
    def download_chapter_body(self, chapter):
        # Download through API
        if self.downloadChapterWithApi:
            ## The URL is already formed with the API! Just take the JSON
            response = self.get_response(chapter["url"]).text
            responseJson = json.loads(response)
            ## The answers yield a list of paragraphs, so iterate through that
            listParagraphs = []
            for paragraph in responseJson["paragraphs"]:
                listParagraphs.append(
                    "<p>" + paragraph["content"] + "</p>"
                )  # HTML format, <p>paragraph</p>
            return "".join(listParagraphs)  # Returns a string with all paragraphs

        # or download through BeautifulSoup
        else:
            # Rework the URL
            url_browser = chapter["url"].replace(
                self.absolute_url(self.apiPath) + "/chapters/", self.absolute_url("/novel") + "/"
            )
            soup = self.get_soup(url_browser)
            content = soup.find(
                "div",
                {
                    "class": "chapter-content",
                },
            )
            return self.cleaner.extract_contents(content)
