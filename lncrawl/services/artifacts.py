from typing import List, Optional

from sqlmodel import and_, asc, desc, func, select

from ..context import ctx
from ..dao import Artifact, OutputFormat, User, UserRole
from ..exceptions import ServerErrors
from ..server.models import Paginated


class ArtifactService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        novel_id: Optional[str] = None,
        format: Optional[OutputFormat] = None,
    ) -> Paginated[Artifact]:
        with ctx.db.session() as sess:
            stmt = select(Artifact)

            # Apply filters
            if novel_id:
                stmt = stmt.where(Artifact.novel_id == novel_id)
            if user_id:
                stmt = stmt.where(Artifact.user_id == user_id)
            if job_id:
                stmt = stmt.where(Artifact.job_id == job_id)
            if format:
                stmt = stmt.where(Artifact.format == format)

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
        with ctx.db.session() as sess:
            artifact = sess.get(Artifact, artifact_id)
            if not artifact:
                raise ServerErrors.no_such_artifact
            return artifact

    def delete(self, artifact_id: str, user: User) -> bool:
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
        with ctx.db.session() as sess:
            artifact = sess.get(Artifact, artifact_id)
            if not artifact:
                raise ServerErrors.no_such_artifact
            ctx.files.resolve(artifact.output_file).unlink(True)
            sess.delete(artifact)
            sess.commit()
            return True

    def get_epub(self, depends_on_job_id: str) -> Artifact:
        with ctx.db.session() as sess:
            artifact = sess.exec(
                select(Artifact).where(Artifact.job_id == depends_on_job_id)
            ).first()
            if not artifact or not artifact.is_available:
                raise ServerErrors.no_epub_file
            return artifact

    def list_latest(self, novel_id: str) -> List[Artifact]:
        with ctx.db.session() as sess:
            subq = (
                select(Artifact.format, func.max(Artifact.updated_at).label("max_updated_at"))
                .where(Artifact.novel_id == novel_id)
                .group_by(Artifact.format)
                .subquery()
            )
            rows = sess.exec(
                select(Artifact)
                .join(
                    subq,
                    and_(
                        Artifact.format == subq.c.format,
                        Artifact.updated_at == subq.c.max_updated_at,
                    ),
                )
                .order_by(asc(Artifact.format))
            ).all()
            return list(rows)

    def get_latest(self, novel_id: str, format: OutputFormat) -> Optional[Artifact]:
        with ctx.db.session() as sess:
            artifact = sess.exec(
                select(Artifact)
                .where(Artifact.novel_id == novel_id)
                .where(Artifact.format == format)
                .order_by(desc(Artifact.updated_at))
                .limit(1)
            ).first()
            return artifact
