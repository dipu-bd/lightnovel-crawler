from typing import List

from sqlmodel import asc, desc, func, select

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.job import Artifact, Novel
from ..models.pagination import Paginated
from ..models.user import User, UserRole


class NovelService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx
        self._db = ctx.db

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        with_orphans: bool = False
    ) -> Paginated[Novel]:
        with self._db.session() as sess:
            stmt = select(Novel)

            # Apply filters
            if not with_orphans:
                stmt = stmt.where(Novel.orphan != True)  # noqa: E712

            # Apply sorting
            stmt.order_by(asc(Novel.title), desc(Novel.created_at))

            total = sess.exec(select(func.count()).select_from(Novel)).one()
            items = sess.exec(stmt.offset(offset).limit(limit)).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def get(self, novel_id: str) -> Novel:
        with self._db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise AppErrors.no_such_novel
            return novel

    def delete(self, novel_id: str, user: User) -> bool:
        if user.role != UserRole.ADMIN:
            raise AppErrors.forbidden
        with self._db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                return True
            sess.delete(novel)
            sess.commit()
            return True

    def get_artifacts(self, novel_id: str) -> List[Artifact]:
        with self._db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise AppErrors.no_such_novel
            return novel.artifacts
