# -*- coding: utf-8 -*-

from typing import Union

from .section import __Section__


class _Browser(__Section__):
    @property
    def concurrent_requests(self) -> int:
        return self.__data__.get('concurrent_requests', 5)

    @concurrent_requests.setter
    def concurrent_requests(self, value: int) -> None:
        self.__data__['concurrent_requests'] = value
        self.save()

    @property
    def soup_parser(self) -> str:
        return self.__data__.get('soup_parser', 'html5lib')

    @soup_parser.setter
    def soup_parser(self, value: str) -> None:
        self.__data__['soup_parser'] = value
        self.save()

    @property
    def response_timeout(self) -> Union[int, float, None]:
        return self.__data__.get('response_timeout', None)

    @response_timeout.setter
    def response_timeout(self, value: int) -> None:
        self.__data__['response_timeout'] = value
        self.save()

    @property
    def stream_chunk_size(self) -> int:
        return self.__data__.get('stream_chunk_size', 10 * 1024)

    @stream_chunk_size.setter
    def stream_chunk_size(self, value: int) -> None:
        self.__data__['stream_chunk_size'] = value
        self.save()

    @property
    def engine(self) -> str:
        return self.__data__.get('engine', 'cloudscraper')

    @property
    def cloudscraper(self) -> dict:
        return self.__data__.get('cloudscraper', {})
