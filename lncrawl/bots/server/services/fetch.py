import httpx
from bs4 import BeautifulSoup

from ..context import ServerContext
from ..exceptions import AppErrors


class FetchService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx

    async def website_title(self, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            BeautifulSoup()

    async def image(self, image_url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code >= 400:
                raise AppErrors.invalid_image_response
            return response
