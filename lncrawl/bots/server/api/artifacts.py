import mimetypes
import os
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Security
from fastapi.responses import FileResponse

from ..security import ensure_user
from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.job import Artifact
from ..models.pagination import Paginated

# The root router
router = APIRouter()


@router.get("s", summary='Returns a list of artifacts',
            dependencies=[Security(ensure_user)],)
def list_artifacts(
    ctx: ServerContext = Depends(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    novel_id: Optional[str] = Query(default=None),
) -> Paginated[Artifact]:
    return ctx.artifacts.list(
        limit=limit,
        offset=offset,
        novel_id=novel_id,
    )


@router.get("/{artifact_id}", summary='Returns a artifact',
            dependencies=[Security(ensure_user)],)
def get_novel(
    artifact_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> Artifact:
    return ctx.artifacts.get(artifact_id)


@router.get("/{artifact_id}/download", summary='Download artifact file')
def get_novel_artifacts(
    artifact_id: str = Path(),
    ctx: ServerContext = Depends(),
) -> FileResponse:
    artifact = ctx.artifacts.get(artifact_id)
    file_path = artifact.output_file
    if not file_path:
        raise AppErrors.no_artifact_file

    media_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type=media_type or "application/octet-stream",
    )
