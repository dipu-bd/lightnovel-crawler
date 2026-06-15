from contextlib import contextmanager
from difflib import SequenceMatcher
import logging
from threading import Event
from typing import List, Optional, Union

from pydantic import HttpUrl

from ..context import ctx
from ..core import Chapter as CrawlerChapter, Crawler, Novel as CrawlerNovel, SearchResult
from ..dao import Chapter, ChapterImage, Novel
from ..exceptions import ServerErrors
from ..utils.url_tools import extract_host

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self) -> None:
        pass

    @contextmanager
    def prepare_crawler(
        self,
        user_id: str,
        url: str,
        signal: Optional[Event] = None,
        custom_crawler: Optional[Crawler] = None,
    ):
        crawler = custom_crawler
        if crawler is None:
            crawler = ctx.sources.init_crawler(url)

        prev_signal = crawler.scraper.signal
        if signal:
            crawler.scraper.signal = signal

        try:
            # login
            can_login = getattr(crawler, "can_login", False)
            logged_in = getattr(crawler, "__logged_in__", False)
            if can_login and not logged_in:
                login = ctx.secrets.get_login(user_id, url)
                if login:
                    crawler.login(login.username, login.password)
                    setattr(crawler, "__logged_in__", True)

            yield crawler

        finally:
            crawler.scraper.signal = prev_signal
            if custom_crawler is None:
                crawler.close()

    def fetch_novel(
        self,
        user_id: str,
        url: Union[str, HttpUrl],
        signal: Optional[Event] = None,
        custom: Optional[Crawler] = None,
    ) -> Novel:
        # validate url
        if isinstance(url, str):
            url = HttpUrl(url)
        if not url.host:
            raise ServerErrors.invalid_url.with_extra(url)
        novel_url = str(url)

        with self.prepare_crawler(user_id, novel_url, signal, custom) as crawler:
            # fetch novel metadata
            model = CrawlerNovel(url=novel_url)
            crawler.read_novel(model)
            if not model.title:
                raise ServerErrors.no_novel_title
            crawler.format_novel(model)
            assert model.volumes is not None
            assert model.chapters is not None

            # get or create novel object
            novel = ctx.novels.find_by_url(novel_url)
            if not novel:
                with ctx.db.session() as sess:
                    novel = Novel(
                        url=novel_url,
                        title=model.title,
                        cover_url=model.cover_url,
                        domain=extract_host(novel_url),
                    )
                    sess.add(novel)
                    sess.commit()

            # update novel info
            novel.title = model.title
            novel.authors = model.author
            novel.cover_url = model.cover_url
            novel.domain = extract_host(novel_url)
            novel.manga = model.is_manga or crawler.has_manga
            novel.mtl = model.is_mtl or crawler.has_mtl
            novel.synopsis = model.synopsis
            novel.tags = model.tags or []
            novel.rtl = model.is_rtl or False
            novel.language = model.language
            novel.volume_count = len(model.volumes)
            novel.chapter_count = len(model.chapters)

            # update novel extra
            extra = dict(**novel.extra)
            extra.update(model.get_extras())
            extra["crawler_version"] = crawler.version
            novel.extra = extra

            # save updates
            with ctx.db.session() as sess:
                sess.merge(novel)
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

            # update output path time (prevents cleaner to delete it)
            ctx.files.utime(f"novels/{novel.id}")

        logger.debug(
            f"Fetched novel: {novel.title} - {novel.chapter_count} chapters | {novel.volume_count} volumes | {novel.url}"
        )
        return novel

    def fetch_chapter(
        self,
        user_id: str,
        chapter_id: str,
        signal: Optional[Event] = None,
        custom: Optional[Crawler] = None,
        refresh: bool = False,
    ) -> Chapter:
        chapter = ctx.chapters.get(chapter_id)
        novel = ctx.novels.get(chapter.novel_id)
        try:
            url = HttpUrl(chapter.url)
        except Exception:
            raise ServerErrors.invalid_url
        if not url.host:
            raise ServerErrors.invalid_url

        with self.prepare_crawler(user_id, novel.url, signal, custom) as crawler:
            # check if download is necessary
            if (
                not refresh
                and chapter.is_available
                and chapter.extra.get("crawler_version") == crawler.version
            ):
                logger.debug(f"Skipped: {novel.title}] - Chapter {chapter.serial}")
                return chapter

            # get chapter content
            model = CrawlerChapter(
                url=str(url),
                id=chapter.serial,
                title=chapter.title,
            )
            model.update(chapter.extra)
            crawler.download_chapter(model)
            crawler.format_chapter(model)
            assert model.body is not None

            # save chapter content
            ctx.files.save_text(chapter.content_file, model.body)

            # save chapter images
            ctx.images.sync(chapter, model.images)

            # set extras
            extra = dict(**chapter.extra)
            extra.update(model.get_extras())
            extra["crawler_version"] = crawler.version
            chapter.extra = extra

            # update title and status
            chapter.is_done = True
            chapter.title = model.title

            # update db
            with ctx.db.session() as sess:
                sess.merge(chapter)
                sess.commit()

            logger.debug(f"Downloaded chapter: {novel.title}] - Chapter {chapter.serial}")
            return chapter

    def fetch_image(
        self,
        user_id: str,
        image_id: str,
        signal: Optional[Event] = None,
        custom: Optional[Crawler] = None,
        refresh: bool = False,
    ) -> ChapterImage:
        image = ctx.images.get(image_id)
        novel = ctx.novels.get(image.novel_id)
        try:
            url = HttpUrl(image.url)
        except Exception:
            raise ServerErrors.invalid_url
        if not url.host:
            raise ServerErrors.invalid_url

        with self.prepare_crawler(user_id, novel.url, signal, custom) as crawler:
            # check if download is necessary
            if (
                not refresh
                and image.is_available
                and image.extra.get("crawler_version") == crawler.version
            ):
                logger.debug(f"Skipped: {novel.title}] - Image {image.id}")
                return image

            # download image
            file = ctx.files.resolve(image.image_file)
            crawler.download_image(str(url), file)

            image.is_done = file.is_file()
            extra = dict(**image.extra)
            extra["crawler_version"] = crawler.version
            image.extra = extra

            # update db
            with ctx.db.session() as sess:
                sess.merge(image)
                sess.commit()

            logger.debug(f"Downloaded image: {novel.title}] - Image {image.id}")
            return image

    def search_novel(
        self,
        user_id: str,
        query: str,
        domain: str,
        signal: Optional[Event] = None,
        custom: Optional[Crawler] = None,
    ) -> List[SearchResult]:
        # get crawler
        source = ctx.sources.get_source(domain)
        with self.prepare_crawler(user_id, source.url, signal, custom) as crawler:
            results = list(crawler.search(query))
            results.sort(key=lambda x: -SequenceMatcher(a=x.title, b=query).ratio())
            return list(results)
