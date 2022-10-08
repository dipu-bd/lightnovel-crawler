import logging
import re
from urllib.parse import urlparse

from slugify import slugify

from ...core.sources import sources_path
from .analyze import analyze_url
from .generator import generate_crawler
from .prompts import get_features, get_novel_url


class LookupBot:
    log = logging.getLogger(__name__)

    def __init__(self) -> None:
        pass

    def start(self) -> None:
        novel_url = get_novel_url()

        _parsed = urlparse(novel_url)
        base_url = "%s://%s/" % (_parsed.scheme, _parsed.hostname)
        name = re.sub(r"(^www\.)|(\.com$)", "", _parsed.hostname)

        template = analyze_url(base_url, novel_url)

        features = get_features()
        language = features["language"] or "multi"
        has_manga = features["has_manga"]
        has_mtl = features["has_mtl"]

        filename = name + ".py"
        classname = slugify(
            name,
            max_length=20,
            separator="_",
            lowercase=True,
            word_boundary=True,
        ).title()

        folder = sources_path / language
        if language == "en":
            folder = folder / filename[0]
        filename = str(folder / filename)

        generate_crawler(
            template,
            output_file=filename,
            classname=classname,
            base_url=base_url,
            has_manga=has_manga,
            has_mtl=has_mtl,
        )
