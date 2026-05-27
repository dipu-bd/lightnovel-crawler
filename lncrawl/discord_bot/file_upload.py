from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Union

import httpx

if TYPE_CHECKING:
    import discord

logger = logging.getLogger(__name__)


def should_upload_to_discord(file_path: Path, max_size_mb: float) -> bool:
    return file_path.stat().st_size <= int(max_size_mb * 1024 * 1024)


def upload_to_fileio(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        response = httpx.post(
            "https://file.io",
            files={"file": (file_path.name, f)},
            timeout=120.0,
        )
    response.raise_for_status()
    data = response.json()
    link = data.get("link")
    if not link:
        raise RuntimeError(f"file.io upload failed: {data}")
    return link


def get_file_delivery(
    file_path: Path,
    max_size_mb: float,
) -> Union["discord.File", str]:
    import discord

    if should_upload_to_discord(file_path, max_size_mb):
        return discord.File(file_path)
    url = upload_to_fileio(file_path)
    logger.info(f"Uploaded {file_path.name} to file.io: {url}")
    return url
