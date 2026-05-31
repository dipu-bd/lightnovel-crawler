import logging
import os
from pathlib import Path
from typing import Union

from ..context import ctx
from ..exceptions import ServerErrors
from ..utils.text_tools import is_compressed, text_compress, text_decompress

logger = logging.getLogger(__name__)

StrPath = Union[str, Path]


class FileService:
    def __init__(self) -> None:
        pass

    @property
    def root(self):
        return ctx.config.app.app_dir

    def resolve(self, file: StrPath) -> Path:
        if isinstance(file, str):
            file = Path(file.lstrip("/"))
        if file.is_absolute():
            return file
        return self.root / file

    def exists(self, file_path: StrPath):
        return self.resolve(file_path).is_file()

    def load(self, file_path: StrPath) -> bytes:
        file = self.resolve(file_path)
        if not file.is_file():
            raise ServerErrors.no_such_file
        return file.read_bytes()

    def save(self, file_path: StrPath, content: bytes) -> Path:
        file = self.resolve(file_path)
        file.parent.mkdir(parents=True, exist_ok=True)
        tmp = file.with_suffix(f"{file.suffix}.tmp")
        try:
            tmp.write_bytes(content)
            os.replace(tmp, file)
        finally:
            tmp.unlink(missing_ok=True)
        return file

    def load_text(
        self,
        file_path: StrPath,
        encoding: str = "utf-8",
    ) -> str:
        data = self.load(file_path)
        if is_compressed(data):
            data = text_decompress(data)
        return data.decode(encoding)

    def save_text(
        self,
        file_path: StrPath,
        content: str,
        compress: bool = True,
        encoding: str = "utf-8",
    ) -> Path:
        data = content.encode(encoding)
        if compress or is_compressed(data):
            data = text_compress(data)
        return self.save(file_path, data)

    def utime(self, file: StrPath) -> None:
        path = self.resolve(file)
        if path.exists():
            os.utime(path)
