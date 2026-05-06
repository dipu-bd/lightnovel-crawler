import logging
import os
import shlex
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Union

from slugify import slugify

from .platforms import Platform

logger = logging.getLogger(__name__)


@contextmanager
def atomic_write(path: Union[str, Path], mode: str = "wb") -> Iterator:
    """Atomically write to `path` via a sibling temp file in the same directory.

    On context exit the temp file is renamed onto the target with `os.replace`,
    which is atomic on POSIX and Windows. On exception the temp file is removed
    and the original (if any) is left untouched.

    Avoids the Windows "[Errno 13] Permission denied" issue you get when
    reopening a `tempfile.NamedTemporaryFile` by path while it is still open.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(fd, mode) as f:
            yield f
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def format_size(num_bytes: int, decimals: int = 1, suffix: str = "B") -> str:
    """
    Convert a size in bytes into a human-readable string representing the size,
    e.g. "117.7 MB" or "9.0 GB".

    Units go up to zettabytes (ZB), then yottabytes (YB) as a fallback.
    """
    units = ["", "K", "M", "G", "T", "P", "E", "Z"]
    size = float(num_bytes)
    for unit in units:
        if abs(size) < 1024.0:
            return f"{size:.{decimals}f} {unit}{suffix}"
        size /= 1024.0
    return f"{size:.{decimals}f} Y{suffix}"


def folder_size(folder: Union[str, Path]) -> int:
    """
    Return the total size of a folder in bytes.

    Uses PowerShell on Windows or `du` on POSIX for speed.
    Falls back to a Python directory walk if the system command fails.
    Returns 0 if the folder does not exist or no files are readable.
    """
    try:
        if Platform.windows:
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-ChildItem -LiteralPath '{folder}' -Recurse -Force -File | Measure-Object Length -Sum).Sum",
            ]
            out = subprocess.check_output(cmd, text=True).strip()
            return int(out) if out else 0
        elif Platform.posix:
            cmd = shlex.split(f'du -s -B1 "{folder}"')
            out = subprocess.check_output(cmd, text=True).strip()
            return int(out.split()[0]) if out else 0
    except Exception:
        logger.warning("System command failed, falling back to Python scan", exc_info=True)

    # Python fallback
    try:
        return sum(f.stat().st_size for f in Path(folder).rglob("*") if f.is_file())
    except Exception:
        logger.error("Failed to calculate folder size in Python fallback", exc_info=True)
        return 0


# Windows reserved device names
_WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def safe_filename(name: str) -> str:
    name = (
        slugify(
            name,
            max_length=255,
            separator=" ",
            regex_pattern=r'[#<>:"/\\|?*\x00-\x1F]',
        ).strip(" .")
        or "untitled"
    )
    if name.upper() in _WINDOWS_RESERVED:
        name = f"_{name}"
    return name or "untitled"


def open_folder(folder_path: Union[str, Path]) -> None:
    if Platform.windows:
        os.system(f'explorer.exe "{folder_path}"')
    elif Platform.wsl:
        os.system(f'cd "{folder_path}" && explorer.exe .')
    elif Platform.linux:
        os.system(f'xdg-open "{folder_path}"')
    elif Platform.mac:
        os.system(f'open "{folder_path}"')
