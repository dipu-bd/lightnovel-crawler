from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from ...context import ctx
from ...dao import Chapter, LanguageCode, Volume

MAX_ARTIFACT_CHAPTERS = 100


@dataclass(frozen=True)
class ArtifactScope:
    mode: str
    label: str
    start_volume_serial: Optional[int] = None
    end_volume_serial: Optional[int] = None
    start_chapter_serial: Optional[int] = None
    end_chapter_serial: Optional[int] = None

    def extra(self) -> Dict[str, Any]:
        return {
            "scope_mode": self.mode,
            "scope_label": self.label,
            "start_volume_serial": self.start_volume_serial,
            "end_volume_serial": self.end_volume_serial,
            "start_chapter_serial": self.start_chapter_serial,
            "end_chapter_serial": self.end_chapter_serial,
        }


def get_artifact_scope(artifact) -> ArtifactScope:
    return ArtifactScope(
        mode=artifact.scope_mode or artifact.extra.get("scope_mode") or "whole_novel",
        label=artifact.scope_label or artifact.extra.get("scope_label") or "",
        start_volume_serial=artifact.start_volume_serial
        or artifact.extra.get("start_volume_serial"),
        end_volume_serial=artifact.end_volume_serial or artifact.extra.get("end_volume_serial"),
        start_chapter_serial=artifact.start_chapter_serial
        or artifact.extra.get("start_chapter_serial"),
        end_chapter_serial=artifact.end_chapter_serial or artifact.extra.get("end_chapter_serial"),
    )


def filter_volumes(volumes: Iterable[Volume], scope: ArtifactScope) -> List[Volume]:
    items = list(volumes)
    if scope.start_volume_serial is None and scope.end_volume_serial is None:
        return items
    start = scope.start_volume_serial or -1
    end = scope.end_volume_serial or 10**12
    return [volume for volume in items if start <= volume.serial <= end]


def filter_chapters(chapters: Iterable[Chapter], scope: ArtifactScope) -> List[Chapter]:
    items = list(chapters)
    if scope.start_chapter_serial is None and scope.end_chapter_serial is None:
        return items
    start = scope.start_chapter_serial or -1
    end = scope.end_chapter_serial or 10**12
    return [chapter for chapter in items if start <= chapter.serial <= end]


def iter_artifact_chapters(
    novel_id: str,
    language: Optional[LanguageCode] = None,
    scope: Optional[ArtifactScope] = None,
) -> Iterable[tuple[Volume, List[Chapter]]]:
    scope = scope or ArtifactScope(mode="whole_novel", label="")
    volumes = filter_volumes(ctx.volumes.list(novel_id, language), scope)
    for volume in volumes:
        chapters = filter_chapters(ctx.chapters.list(volume_id=volume.id, language=language), scope)
        if chapters:
            yield volume, chapters


def resolve_artifact_scopes(novel_id: str, data: Dict[str, Any]) -> List[ArtifactScope]:
    mode = data.get("scope_mode") or "by_volume"
    volumes = ctx.volumes.list(novel_id)
    chapters_by_volume = {volume.id: ctx.chapters.list(volume_id=volume.id) for volume in volumes}

    if mode == "volume_ids":
        volume_ids = set(data.get("volume_ids") or [])
        volumes = [volume for volume in volumes if volume.id in volume_ids]
    elif mode == "volume_range":
        start = data.get("from_volume")
        end = data.get("to_volume")
        if start is not None and end is not None and start > end:
            start, end = end, start
        volumes = [
            volume
            for volume in volumes
            if (start is None or volume.serial >= start) and (end is None or volume.serial <= end)
        ]
    elif mode == "chapter_range":
        return _chunk_chapter_range(novel_id, data)
    elif mode != "by_volume":
        return []

    scopes: List[ArtifactScope] = []
    for volume in volumes:
        chunks = _chunk_chapters(chapters_by_volume.get(volume.id) or [])
        for index, chunk in enumerate(chunks, 1):
            label = f"Volume {volume.serial}"
            if len(chunks) > 1:
                label += f" Part {index}"
            scopes.append(
                ArtifactScope(
                    mode=mode,
                    label=label,
                    start_volume_serial=volume.serial,
                    end_volume_serial=volume.serial,
                    start_chapter_serial=chunk[0].serial,
                    end_chapter_serial=chunk[-1].serial,
                )
            )
    return scopes


def _chunk_chapter_range(novel_id: str, data: Dict[str, Any]) -> List[ArtifactScope]:
    start = data.get("from_chapter")
    end = data.get("to_chapter")
    chapters = ctx.chapters.list(novel_id=novel_id)
    if start is not None and end is not None and start > end:
        start, end = end, start
    chapters = [
        chapter
        for chapter in chapters
        if (start is None or chapter.serial >= start) and (end is None or chapter.serial <= end)
    ]

    scopes: List[ArtifactScope] = []
    for chunk in _chunk_chapters(chapters):
        volume_serials = _volume_serials(chunk)
        scopes.append(
            ArtifactScope(
                mode="chapter_range",
                label=f"Chapters {chunk[0].serial}-{chunk[-1].serial}",
                start_volume_serial=min(volume_serials) if volume_serials else None,
                end_volume_serial=max(volume_serials) if volume_serials else None,
                start_chapter_serial=chunk[0].serial,
                end_chapter_serial=chunk[-1].serial,
            )
        )
    return scopes


def _chunk_chapters(chapters: List[Chapter]) -> List[List[Chapter]]:
    chapters = sorted(chapters, key=lambda chapter: chapter.serial)
    return [
        chapters[index : index + MAX_ARTIFACT_CHAPTERS]
        for index in range(0, len(chapters), MAX_ARTIFACT_CHAPTERS)
    ]


def _volume_serials(chapters: List[Chapter]) -> List[int]:
    if not chapters:
        return []
    volume_ids = {chapter.volume_id for chapter in chapters if chapter.volume_id}
    volumes = ctx.volumes.get_many(list(volume_ids))
    return [volume.serial for volume in volumes]
