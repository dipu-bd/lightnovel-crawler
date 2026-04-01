import gzip
import hashlib
import importlib.util
import inspect
import io
import json
import logging
import shutil
from pathlib import Path
from typing import Generator, Type

from ...context import ctx
from ...core.crawler import Crawler
from ...server.models import CrawlerIndex, CrawlerInfo
from ...utils.url_tools import validate_url

logger = logging.getLogger(__name__)


def load_source(file: Path) -> CrawlerIndex:
    json_str = file.read_text(encoding="utf-8")
    return CrawlerIndex.model_validate_json(json_str)


def save_source(file: Path, content: CrawlerIndex):
    file.parent.mkdir(parents=True, exist_ok=True)
    json_str = content.model_dump_json(indent=2)
    file.write_text(json_str, encoding="utf-8")


def fetch_online_source() -> CrawlerIndex:
    compressed = ctx.http.get(ctx.config.crawler.index_file_download_url)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as fp:
        json_str = fp.read().decode()
        return CrawlerIndex.model_validate_json(json_str)


def load_offline_source(check_user=True) -> CrawlerIndex:
    # get local index
    local_file = ctx.config.crawler.local_index_file
    local_index = load_source(local_file)

    # get local rejected
    rejected_file = local_file.parent / "_rejected.json"
    if rejected_file.is_file():
        json_str = rejected_file.read_text(encoding="utf-8")
        local_index.rejected = json.loads(json_str)

    if not check_user:
        return local_index

    # get user index. use local index if not available
    user_file = ctx.config.crawler.user_index_file
    if not user_file.is_file():
        user_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_file, user_file)
        return local_index
    user_index = load_source(user_file)

    # check latest index. use local index if it is latest
    if user_index.v < local_index.v:
        shutil.copy2(local_file, user_file)
        return local_index

    return user_index


def has_method(crawler: Type[Crawler], method: str):
    """Checks if crawler has a callable method"""
    return hasattr(crawler, method) and callable(getattr(crawler, method))


def batch_import_crawlers(*files: Path):
    return (crawler for file in files if file.is_file() for crawler in import_crawlers(file))


def import_crawlers(file: Path) -> Generator[Type[Crawler], None, None]:
    # validate the file
    if not file.is_file():
        return
    if file.name.startswith("_") or not file.name[0].isalnum():
        return
    file = file.absolute()

    # import modules from the file
    try:
        mod_name = hashlib.md5(file.name.encode()).hexdigest()
        spec = importlib.util.spec_from_file_location(mod_name, file)
        if not (spec and spec.loader):
            logger.info(f"\\[{file}] Unexpected spec")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        logger.info(f"\\[{file}] Failed to load: {repr(e)}")
        return

    # import all valid crawlers
    for key in dir(module):
        crawler = getattr(module, key)

        # type checks
        if (
            crawler is Crawler
            or type(crawler) is not type(Crawler)
            or not issubclass(crawler, Crawler)
            or crawler.__dict__.get("is_template")
            or getattr(crawler, "__module__", "") != mod_name
        ):
            continue

        if inspect.isabstract(crawler):
            logger.info(f"\\[{file}] Incomplete or abstract crawler: {crawler}")
            continue

        # base url checks
        base_url = getattr(crawler, "base_url", [])
        urls = [base_url] if isinstance(base_url, str) else base_url
        urls = [str(url).lower().strip("/") + "/" for url in urls]
        urls = [url for url in set(urls) if validate_url(url)]
        if not urls:
            logger.info(f"\\[{file}] No base url: {crawler}")
            continue
        crawler.base_url = urls

        # other metdata
        stat = file.stat()
        id = hashlib.md5(str(crawler).encode()).hexdigest()
        setattr(crawler, "__id__", id)
        setattr(crawler, "__file__", str(file))
        setattr(crawler, "__module_obj__", module)
        setattr(crawler, "version", int(max(stat.st_mtime, stat.st_ctime)))

        yield crawler


def create_crawler_info(crawler: Type[Crawler]):
    root = ctx.config.crawler.local_sources.parent
    file = Path(getattr(crawler, "__file__"))
    file_path = file.relative_to(root).as_posix()
    language = file_path.split("/")[1]
    return CrawlerInfo(
        language=language,
        file_path=file_path,
        id=getattr(crawler, "__id__"),
        md5=getattr(crawler, "__module__"),
        base_urls=getattr(crawler, "base_url"),
        version=int(getattr(crawler, "version")),
        has_mtl=crawler.has_mtl,
        has_manga=crawler.has_manga,
        can_login=crawler.can_login,
        can_search=crawler.can_search,
        url=f"file:///{Path(file).resolve().as_posix()}",
    )
