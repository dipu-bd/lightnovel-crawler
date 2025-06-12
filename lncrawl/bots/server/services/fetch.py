import io

import httpx
from bs4 import BeautifulSoup
from fastapi.responses import StreamingResponse

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

    async def image(self, image_url: str) -> StreamingResponse:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code >= 400:
                raise AppErrors.invalid_image_response

        content_type = response.headers.get("Content-Type")
        if not content_type:
            raise AppErrors.invalid_image_response

        return StreamingResponse(
            content=io.BytesIO(response.content),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=31536000, immutable"
            }
        )
