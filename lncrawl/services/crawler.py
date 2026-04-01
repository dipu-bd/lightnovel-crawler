import logging
from threading import Event
from typing import Optional, Union

from pydantic import HttpUrl
from sqlmodel import select

from ..context import ctx
from ..core import Chapter as CrawlerChapter
from ..core import Crawler
from ..core import Novel as CrawlerNovel
from ..core.models import get_extras
from ..dao import Chapter, ChapterImage, Novel
from ..exceptions import ServerErrors

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self) -> None:
        pass

    def get_crawler(self, user_id: str, novel_url: str):
        constructor = ctx.sources.get_crawler(novel_url)
        crawler = ctx.sources.init_crawler(constructor)
        crawler.novel_url = novel_url
        can_login = getattr(crawler, "can_login", False)
        logged_in = getattr(crawler, "__logged_in__", False)
        if can_login and not logged_in:
            login = ctx.secrets.get_login(user_id, novel_url)
            if login:
                crawler.login(login.username, login.password)
                setattr(crawler, "__logged_in__", True)
        return crawler

    def fetch_novel(
        self,
        user_id: str,
        url: Union[str, HttpUrl],
        signal=Event(),
        crawler: Optional[Crawler] = None,
    ) -> Novel:
        # validate url
        if isinstance(url, str):
            url = HttpUrl(url)
        if not url.host:
            raise ServerErrors.invalid_url.with_extra(url)
        novel_url = str(url)

        # get crawler
        can_close = False
        if crawler is None:
            crawler = self.get_crawler(user_id, novel_url)
            can_close = True
        crawler.scraper.signal = signal

        # fetch novel metadata
        model = CrawlerNovel(url=novel_url)
        crawler.read_novel(model)
        if not model.title:
            raise ServerErrors.no_novel_title
        crawler.format_novel(model)
        assert model.volumes is not None
        assert model.chapters is not None

        # save to database
        with ctx.db.session() as sess:
            # get or create novel
            novel = sess.exec(select(Novel).where(Novel.url == novel_url)).first()
            if not novel:
                novel = Novel(
                    url=novel_url,
                    domain=url.host,
                    title=model.title,
                )

            # update novel
            novel.title = model.title
            novel.authors = model.author
            novel.cover_url = model.cover_url
            novel.manga = model.is_manga or crawler.has_manga
            novel.mtl = model.is_mtl or crawler.has_mtl
            novel.synopsis = model.synopsis
            novel.tags = model.tags or []
            novel.rtl = model.is_rtl or False
            novel.language = model.language
            novel.volume_count = len(model.volumes)
            novel.chapter_count = len(model.chapters)
            novel.extra.update(get_extras(model))
            sess.add(novel)
            sess.commit()

        # add or update tags
        ctx.tags.insert(novel.tags)

        # add or update volumes
        ctx.volumes.sync(novel.id, model.volumes)

        # add or update chapters
        ctx.chapters.sync(novel.id, model.chapters)

        # download cover
        crawler.download_cover(
            novel.cover_url or "",
            ctx.files.resolve(novel.cover_file),
        )

        # update output path time
        ctx.files.utime(f"novels/{novel.id}")

        # close crawler
        if can_close:
            crawler.close()

        return novel

    def fetch_chapter(
        self,
        user_id: str,
        chapter_id: str,
        signal=Event(),
        crawler: Optional[Crawler] = None,
        refresh: bool = False,
    ) -> Chapter:
        chapter = ctx.chapters.get(chapter_id)
        url = HttpUrl(chapter.url)
        if not url.host:
            raise ServerErrors.invalid_url

        # get crawler
        can_close = False
        if crawler is None:
            novel_url = ctx.novels.get(chapter.novel_id).url
            crawler = self.get_crawler(user_id, novel_url)
            can_close = True
        crawler_version = getattr(crawler, "version")
        crawler.scraper.signal = signal

        # check if download is necessary
        if (
            not refresh
            and chapter.is_available
            and chapter.extra.get("crawler_version") == crawler_version
        ):
            return chapter

        # get chapter content
        model = CrawlerChapter(
            url=str(url),
            id=chapter.serial,
            title=chapter.title,
            extras=chapter.extra,
        )
        crawler.download_chapter(model)
        crawler.format_chapter(model)
        assert model.body is not None

        # save chapter content
        ctx.files.save_text(chapter.content_file, model.body)

        # save chapter images
        ctx.images.sync(chapter, model.images)

        # update db
        with ctx.db.session() as sess:
            chapter.is_done = True
            chapter.title = model.title
            chapter.extra.update(get_extras(model))
            sess.add(chapter)
            sess.commit()

        # close crawler
        if can_close:
            crawler.close()

        return chapter

    def fetch_image(
        self,
        user_id: str,
        image_id: str,
        signal=Event(),
        crawler: Optional[Crawler] = None,
        refresh: bool = False,
    ) -> ChapterImage:
        image = ctx.images.get(image_id)
        url = HttpUrl(image.url)
        if not url.host:
            raise ServerErrors.invalid_url

        # get crawler
        can_close = False
        if crawler is None:
            novel_url = ctx.novels.get(image.novel_id).url
            crawler = self.get_crawler(user_id, novel_url)
            can_close = True
        crawler_version = getattr(crawler, "version")
        crawler.scraper.signal = signal

        # check if download is necessary
        if (
            not refresh
            and image.is_available
            and image.extra.get("crawler_version") == crawler_version
        ):
            return image

        # download image
        file = ctx.files.resolve(image.image_file)
        crawler.download_image(str(url), file)

        # update db
        with ctx.db.session() as sess:
            image.is_done = file.is_file()
            image.extra["crawler_version"] = crawler_version
            sess.add(image)
            sess.commit()

        # close crawler
        if can_close:
            crawler.close()

        return image
