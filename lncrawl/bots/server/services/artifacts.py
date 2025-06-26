import os
from typing import Optional

from sqlmodel import desc, func, select

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.enums import UserRole
from ..models.novel import Artifact
from ..models.pagination import Paginated
from ..models.user import User


class ArtifactService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx
        self._db = ctx.db

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        novel_id: Optional[str] = None,
    ) -> Paginated[Artifact]:
        with self._db.session() as sess:
            stmt = select(Artifact)

            # Apply filters
            if not novel_id:
                stmt = stmt.where(Artifact.novel_id == novel_id)

            # Apply sorting
            stmt = stmt.order_by(desc(Artifact.updated_at))

            total = sess.exec(select(func.count()).select_from(Artifact)).one()
            items = sess.exec(stmt.offset(offset).limit(limit)).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def get(self, artifact_id: str) -> Artifact:
        with self._db.session() as sess:
            artifact = sess.get(Artifact, artifact_id)
            if not artifact:
                raise AppErrors.no_such_artifact
            return artifact

    def delete(self, artifact_id: str, user: User) -> bool:
        if user.role != UserRole.ADMIN:
            raise AppErrors.forbidden
        with self._db.session() as sess:
            artifact = sess.get(Artifact, artifact_id)
            if not artifact:
                raise AppErrors.no_such_artifact
            sess.delete(artifact)
            sess.commit()
            return True

    def upsert(self, item: Artifact):
        old_file = None
        new_file = item.output_file

        with self._db.session() as sess:
            artifact = sess.exec(
                select(Artifact)
                .where(Artifact.novel_id == item.novel_id)
                .where(Artifact.format == item.format)
            ).first()

            if not artifact:
                sess.add(item)
            else:
                # update values
                old_file = artifact.output_file
                artifact.job_id = item.job_id
                artifact.output_file = item.output_file
                sess.add(artifact)

            sess.commit()

        # remove old file
        if old_file and old_file != new_file and os.path.isfile(old_file):
            os.remove(old_file)
