from typing import List, Optional

import sqlmodel as sq

from ..context import ctx
from ..dao import Artifact, LanguageCode, OutputFormat, User, UserRole
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
        language: Optional[LanguageCode] = None,
        volume: Optional[int] = None,
    ) -> Paginated[Artifact]:
        with ctx.db.session() as sess:
            stmt = sq.select(Artifact)
            cnt = sq.select(sq.func.count()).select_from(Artifact)

            # Apply filters
            if novel_id:
                stmt = stmt.where(Artifact.novel_id == novel_id)
                cnt = cnt.where(Artifact.novel_id == novel_id)

            if user_id:
                stmt = stmt.where(Artifact.user_id == user_id)
                cnt = cnt.where(Artifact.user_id == user_id)

            if job_id:
                stmt = stmt.where(Artifact.job_id == job_id)
                cnt = cnt.where(Artifact.job_id == job_id)

            if format:
                stmt = stmt.where(Artifact.format == format)
                cnt = cnt.where(Artifact.format == format)

            if language:
                stmt = stmt.where(Artifact.language == language)
                cnt = cnt.where(Artifact.language == language)

            if volume is not None:
                stmt = stmt.where(Artifact.volume == volume)
                cnt = cnt.where(Artifact.volume == volume)

            # Apply sorting
            stmt = stmt.order_by(sq.desc(Artifact.updated_at))

            stmt = stmt.offset(offset)
            stmt = stmt.limit(limit)

            items = sess.exec(stmt).all()
            total = sess.exec(cnt).one()

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
                sq.select(Artifact).where(Artifact.job_id == depends_on_job_id)
            ).first()
            if not artifact or not artifact.is_available:
                raise ServerErrors.no_epub_file
            return artifact

    def list_latest(
        self,
        novel_id: str,
        language: Optional[LanguageCode] = None,
        volume: Optional[int] = None,
    ) -> List[Artifact]:
        with ctx.db.session() as sess:
            subq = (
                sq.select(Artifact.format, sq.func.max(Artifact.updated_at).label("max_updated_at"))
                .where(
                    Artifact.novel_id == novel_id,
                    Artifact.language == language,
                    self._volume_filter(volume),
                )
                .group_by(Artifact.format)
                .subquery()
            )
            rows = sess.exec(
                sq.select(Artifact)
                .join(
                    subq,
                    sq.and_(
                        Artifact.format == subq.c.format,
                        Artifact.updated_at == subq.c.max_updated_at,
                    ),
                )
                # re-apply the same filters on the outer row so a different
                # novel/language/volume sharing (format, updated_at) can't leak in
                .where(
                    Artifact.novel_id == novel_id,
                    Artifact.language == language,
                    self._volume_filter(volume),
                )
                .order_by(sq.asc(Artifact.format))
            ).all()
            return list(rows)

    def get_latest(
        self,
        novel_id: str,
        format: OutputFormat,
        volume: Optional[int] = None,
    ) -> Optional[Artifact]:
        with ctx.db.session() as sess:
            artifact = sess.exec(
                sq.select(Artifact)
                .where(Artifact.novel_id == novel_id)
                .where(Artifact.format == format)
                .where(self._volume_filter(volume))
                .order_by(sq.desc(Artifact.updated_at))
                .limit(1)
            ).first()
            return artifact

    @staticmethod
    def _volume_filter(volume: Optional[int]):
        """Match a specific volume when given, else whole-novel artifacts only."""
        if volume is not None:
            return Artifact.volume == volume
        return sq.col(Artifact.volume).is_(None)
