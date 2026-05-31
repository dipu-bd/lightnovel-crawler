from functools import cached_property
import logging
import shutil
from threading import Event
from typing import Callable, Dict, Optional, Set

from ...context import ctx
from ...dao import Artifact, LanguageCode, OutputFormat
from ...exceptions import ServerErrors
from ...utils.file_tools import safe_filename
from .calibre import convert_epub, is_calibre_available
from .epub import make_epub
from .json import make_json
from .text import make_text

logger = logging.getLogger(__name__)

requires_zip = set(
    [
        OutputFormat.json,
        OutputFormat.text,
    ]
)
archive_maker: Dict[OutputFormat, Callable[..., None]] = {
    OutputFormat.json: make_json,
    OutputFormat.text: make_text,
    OutputFormat.epub: make_epub,
    OutputFormat.docx: convert_epub,
    OutputFormat.mobi: convert_epub,
    OutputFormat.pdf: convert_epub,
    OutputFormat.rtf: convert_epub,
    OutputFormat.azw3: convert_epub,
    OutputFormat.fb2: convert_epub,
    OutputFormat.lit: convert_epub,
    OutputFormat.lrf: convert_epub,
    OutputFormat.pdb: convert_epub,
    OutputFormat.rb: convert_epub,
    OutputFormat.tcr: convert_epub,
}


class BinderService:
    def __init__(self):
        pass

    @cached_property
    def depends_on_epub(self) -> Set[OutputFormat]:
        return set([k for k, v in archive_maker.items() if v == convert_epub])

    @cached_property
    def available_formats(self) -> Set[OutputFormat]:
        all_formats = set(OutputFormat)
        if is_calibre_available():
            return all_formats
        return all_formats - self.depends_on_epub

    def make_artifact(
        self,
        novel_id: str,
        novel_title: str,
        format: OutputFormat,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        epub: Optional[Artifact] = None,
        language: Optional[LanguageCode] = None,
        signal=Event(),
    ) -> Artifact:
        make = archive_maker[format]
        if not callable(make):
            raise ServerErrors.format_not_available

        file_name = safe_filename(novel_title).title()
        if language:
            file_name += f".{language}"
        file_name += f".{format}"
        if format in requires_zip:
            file_name += ".zip"

        artifact = Artifact(
            novel_id=novel_id,
            user_id=user_id,
            job_id=job_id,
            format=format,
            language=language,
            file_name=file_name,
        )

        working_dir = ctx.config.app.app_dir / "tmp" / artifact.id
        try:
            shutil.rmtree(working_dir, True)
            working_dir.mkdir(parents=True)
            make(working_dir, signal=signal, artifact=artifact, epub=epub)
            file = ctx.files.resolve(artifact.output_file)
            if file.is_file():
                artifact.file_size = file.stat().st_size
            with ctx.db.session() as sess:
                sess.add(artifact)
                sess.commit()
                return artifact
        finally:
            shutil.rmtree(working_dir, True)
