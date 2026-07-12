from typing import Any, List, Optional

from sqlmodel import and_, asc, col, delete, func, insert as sa_insert, select

from ..context import ctx
from ..dao import NovelTag, Tag
from ..exceptions import ServerErrors
from ..server.models import Paginated


class TagService:
    def __init__(self) -> None:
        pass

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str = "",
    ) -> Paginated[Tag]:
        with ctx.db.session() as sess:
            stmt = select(Tag)
            cnt = select(func.count()).select_from(Tag)

            # Apply filters
            conditions: List[Any] = []

            if search:
                conditions.append(col(Tag.name).ilike(f"%{search}%"))

            if conditions:
                cnd = and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            stmt = stmt.order_by(asc(Tag.name))

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

    def get(self, name: str) -> Tag:
        with ctx.db.session() as sess:
            tag = sess.get(Tag, name)
            if not tag:
                raise ServerErrors.no_such_tag
            return tag

    def update(self, name: str, description: Optional[str] = None) -> Tag:
        with ctx.db.session() as sess:
            tag = sess.get(Tag, name)
            if not tag:
                raise ServerErrors.no_such_tag
            if description is not None:
                tag.description = description
                sess.commit()
            return tag

    def delete(self, name: str) -> bool:
        with ctx.db.session() as sess:
            tag = sess.get(Tag, name)
            if not tag:
                return True
            sess.delete(tag)
            sess.commit()
            return True

    def insert(self, names: List[str]) -> None:
        with ctx.db.session() as sess:
            existing = sess.exec(select(Tag.name).where(col(Tag.name).in_(names))).all()
            missing = set(names) - set(existing)
            if missing:
                sess.exec(sa_insert(Tag), params=[Tag(name=name).model_dump() for name in missing])
                sess.commit()

    def set_novel_tags(self, novel_id: str, tags: List[str]) -> None:
        """Update the tag vocabulary and replace a novel's tag associations."""
        cleaned = sorted({t.strip() for t in tags if t and t.strip()})
        self.insert(cleaned)
        with ctx.db.session() as sess:
            sess.exec(
                delete(NovelTag).where(
                    col(NovelTag.novel_id) == novel_id,
                )
            )
            if cleaned:
                sess.exec(
                    sa_insert(NovelTag),
                    params=[
                        NovelTag(
                            novel_id=novel_id,
                            tag_name=name,
                        ).model_dump()
                        for name in cleaned
                    ],
                )
            sess.commit()
