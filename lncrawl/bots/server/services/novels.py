from typing import List, Any

from sqlmodel import func, select, and_, not_

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.novel import Artifact, Novel
from ..models.pagination import Paginated
from ..models.user import User, UserRole


class NovelService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx
        self._db = ctx.db

    def list(
        self,
        search: str = '',
        offset: int = 0,
        limit: int = 20,
        with_orphans: bool = False
    ) -> Paginated[Novel]:
        with self._db.session() as sess:
            stmt = select(Novel)
            cnt = select(func.count()).select_from(Novel)

            # Apply filters
            conditions: List[Any] = []
            if not with_orphans:
                conditions.append(not_(Novel.orphan))
                conditions.append(Novel.title != '...')
                conditions.append(Novel.title != '')

            if search:
                conditions.append(
                    func.lower(Novel.title).like(f"%{search.lower()}%")
                )

            if conditions:
                stmt = stmt.where(and_(*conditions))
                cnt = cnt.where(and_(*conditions))

            # Apply sorting
            stmt = stmt.order_by(func.lower(Novel.title).asc())

            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)

            total = sess.exec(cnt).one()
            items = sess.exec(stmt).all()

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
            artifacts = sess.exec(
                select(Artifact).where(Artifact.novel_id == novel.id)
            ).all()
            return list(artifacts)
