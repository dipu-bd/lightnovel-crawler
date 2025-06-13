import io
import base64
import json
import logging
from PIL import Image
from functools import lru_cache
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.responses import FileResponse

from lncrawl.core.app import App
from lncrawl.core.download_chapters import get_chapter_file
from lncrawl.core.metadata import get_metadata_list
from lncrawl.core.sources import crawler_list, rejected_sources

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.meta import SupportedSource
from ..models.novel import (Novel, NovelChapter, NovelChapterContent,
                            NovelVolume)

logger = logging.getLogger(__name__)

# The root router
router = APIRouter()


class MetadataService:
    def __init__(self, ctx: ServerContext) -> None:
        self.ctx = ctx

    @lru_cache()
    def list_supported_sources(self):
        # load_sources()
        supported: Dict[str, SupportedSource] = {}
        for crawler in crawler_list.values():
            for url in crawler.base_url:
                no_www = url.replace("://www.", "://")
                domain = urlparse(no_www).hostname
                if not domain:
                    continue
                supported[domain] = SupportedSource(
                    url=url,
                    domain=domain,
                    has_manga=crawler.has_manga,
                    has_mtl=crawler.has_mtl,
                    is_disabled=(url in rejected_sources),
                    disable_reason=rejected_sources.get(domain) or '',
                    language=crawler.language,
                    can_login=getattr(crawler, 'can_login', False),
                    can_logout=getattr(crawler, 'can_logout', False),
                    can_search=getattr(crawler, 'can_search', False),
                )
        return list(sorted(supported.values(), key=lambda x: x.domain))

    @lru_cache()
    def resolve_output_path(self, novel_id: str):
        with self.ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise AppErrors.no_such_novel

            output_path = novel.extra.get('output_path')
            if output_path and Path(output_path).is_dir():
                return output_path

            if not novel.title:
                raise AppErrors.no_novel_title

            with App() as app:
                app.user_input = novel.url
                app.prepare_search()

                crawler = app.crawler
                if not crawler:
                    logger.error(f'No crawler for: {novel.url}')
                    raise AppErrors.internal_error

                crawler.novel_url = novel.url
                crawler.novel_title = novel.title
                app.prepare_novel_output_path()

                output_path = app.output_path

            if not output_path or not Path(output_path).is_dir():
                raise AppErrors.no_novel_output_path

            if novel.extra.get('output_path') != output_path:
                novel.extra = dict(novel.extra)
                novel.extra['output_path'] = output_path
                sess.add(novel)
                sess.commit()

            return output_path

    def get_novel_toc(self, novel_id: str):
        output_path = self.resolve_output_path(novel_id)
        for meta in get_metadata_list(output_path):
            if meta.novel and meta.session:
                break
        else:
            logger.error(f'No metadata for: {novel_id}')
            raise AppErrors.not_found

        volumes: Dict[int, NovelVolume] = {}
        for vol in meta.novel.volumes:
            volumes[vol.id] = NovelVolume(
                id=vol.id,
                title=vol.title,
            )

        for chap in meta.novel.chapters:
            if not chap.volume or not chap.success:
                continue

            volume = volumes.get(chap.volume)
            if not volume:
                continue

            json_file = get_chapter_file(
                chapter=chap,
                output_path=output_path,
                pack_by_volume=meta.session.pack_by_volume,
            )

            relative_path = str(json_file.relative_to(output_path))
            hash = base64.urlsafe_b64encode(relative_path.encode()).decode()

            volume.chapters.append(
                NovelChapter(
                    id=chap.id,
                    title=chap.title,
                    hash=hash,
                )
            )

        return list(volumes.values())

    def get_novel_chapter_content(self, novel_id: str, hash: str):
        novel = self.ctx.novels.get(novel_id)
        output_path = novel.extra.get('output_path')
        if not output_path:
            raise AppErrors.no_novel_output_path

        file_path = base64.urlsafe_b64decode(hash).decode()
        json_file = (Path(output_path) / file_path).resolve()
        if not json_file.is_file():
            raise AppErrors.not_found

        with open(json_file, 'r', encoding='utf-8') as fp:
            content = json.load(fp)
            if not isinstance(content, dict):
                raise AppErrors.malformed_json_file
            return NovelChapterContent(
                id=content['id'],
                body=content['body'],
                title=content['title'],
                volume_id=content['volume'],
                volume=content['volume_title'],
            )

    async def get_novel_cover(self, novel_id: str):
        with self.ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise AppErrors.no_such_novel
            cover_url = novel.cover

        output_path = self.resolve_output_path(novel_id)
        file_path = Path(output_path) / 'cover.jpg'
        if not file_path.is_file():
            if not cover_url or not cover_url.startswith('http'):
                raise AppErrors.no_novel_cover

            response = await self.ctx.fetch.image(cover_url)
            content_type = response.headers.get("Content-Type")
            if not content_type:
                raise AppErrors.invalid_image_response

            with Image.open(io.BytesIO(response.content)) as img:
                if img.mode not in ("L", "RGB", "YCbCr", "RGBX"):
                    if img.mode == "RGBa":
                        img.convert("RGBA").convert("RGB")
                    else:
                        img.convert("RGB")
                img.save(file_path.as_posix(), "JPEG", optimized=True)

        return FileResponse(
            file_path,
            media_type='image/jpeg',
            headers={
                "Cache-Control": "public, max-age=31536000, immutable"
            }
        )
