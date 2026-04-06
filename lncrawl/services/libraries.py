from typing import List, Optional

import sqlmodel as sa

from ..context import ctx
from ..dao import Library, LibraryNovel, Novel, User, UserRole
from ..exceptions import ServerErrors
from ..server.models import LibraryItem, Paginated


class LibraryService:
    def __init__(self) -> None:
        pass

    def _get_library(self, sess, library_id: str) -> Library:
        library = sess.get(Library, library_id)
        if not library:
            raise ServerErrors.no_such_library
        return library

    def _ensure_owner(self, library: Library, user: User):
        if library.user_id != user.id and user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden

    def _ensure_visible(self, library: Library, user: User):
        if library.is_public or library.user_id == user.id or user.role == UserRole.ADMIN:
            return
        raise ServerErrors.forbidden

    def list_page(
        self,
        offset: int = 0,
        limit: int = 20,
        *,
        query: str = "",
        public_only: bool = False,
        user_id: Optional[str] = None,
    ) -> Paginated[Library]:
        with ctx.db.session() as sess:
            stmt = sa.select(Library)
            cnt = sa.select(sa.func.count()).select_from(Library)

            if user_id:
                stmt = stmt.where(Library.user_id == user_id)
                cnt = cnt.where(Library.user_id == user_id)

            if public_only:
                stmt = stmt.where(sa.col(Library.is_public).is_(True))
                cnt = cnt.where(sa.col(Library.is_public).is_(True))

            if query:
                q = f"%{query.lower()}%"
                stmt = stmt.where(sa.col(Library.name).ilike(q))
                cnt = cnt.where(sa.col(Library.name).ilike(q))

            stmt = stmt.order_by(sa.desc(Library.updated_at))

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

    def list_all(
        self,
        user_id: Optional[str] = None,
    ) -> List[LibraryItem]:
        with ctx.db.session() as sess:
            stmt = sa.select(Library)
            if user_id:
                stmt = stmt.where(Library.user_id == user_id)
            stmt = stmt.order_by(sa.desc(Library.updated_at))
            libraries = sess.exec(stmt).all()
            return [
                LibraryItem(
                    id=library.id,
                    name=library.name,
                    is_public=library.is_public,
                    description=library.description,
                )
                for library in libraries
            ]

    def create(
        self,
        user: User,
        name: str,
        description: Optional[str] = None,
        is_public: bool = False,
    ) -> Library:
        with ctx.db.session() as sess:
            library = Library(
                user_id=user.id,
                name=name.strip(),
                description=description.strip() if description else None,
                is_public=is_public,
                extra={
                    "novel_count": 0,
                    "owner_name": user.name,
                },
            )
            sess.add(library)
            sess.commit()
            return library

    def update(
        self,
        library_id: str,
        user: User,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Library:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)

            if name is not None:
                library.name = name.strip()

            if description is not None:
                library.description = description.strip() if description else None

            if is_public is not None:
                library.is_public = is_public

            owner = sess.get_one(User, library.user_id)
            if library.extra.get("owner_name") != owner.name:
                extra = library.extra.copy()
                extra["owner_name"] = owner.name
                library.extra = extra

            sess.commit()
            return library

    def delete(self, library_id: str, user: User) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)
            sess.delete(library)
            sess.commit()
            return True

    def get(self, library_id: str, user: User) -> Library:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_visible(library, user)

            owner = sess.get_one(User, library.user_id)
            if library.extra.get("owner_name") != owner.name:
                extra = library.extra.copy()
                extra["owner_name"] = owner.name
                library.extra = extra
                sess.commit()

            return library

    def list_novels(
        self,
        library_id: str,
        user: User,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> Paginated[Novel]:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_visible(library, user)

            cnt = (
                sa.select(sa.func.count())
                .select_from(LibraryNovel)
                .where(LibraryNovel.library_id == library_id)
            )
            stmt = (
                sa.select(Novel)
                .join(LibraryNovel, sa.col(LibraryNovel.novel_id) == sa.col(Novel.id))
                .where(LibraryNovel.library_id == library_id)
                .order_by(sa.desc(Novel.updated_at))
                .offset(offset)
                .limit(limit)
            )

            total = sess.exec(cnt).one()
            items = sess.exec(stmt).all()

            if library.extra.get("novel_count") != total:
                extra = library.extra.copy()
                extra["novel_count"] = total
                library.extra = extra
                sess.commit()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def add_novel(self, library_id: str, user: User, novel_id: str) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)

            novel = sess.get(Novel, novel_id)
            if not novel:
                raise ServerErrors.no_such_novel

            existing = sess.scalar(
                sa.select(LibraryNovel).where(
                    LibraryNovel.library_id == library_id,
                    LibraryNovel.novel_id == novel_id,
                )
            )
            if existing:
                return True

            link = LibraryNovel(library_id=library_id, novel_id=novel_id)
            sess.add(link)

            extra = library.extra.copy()
            extra["novel_count"] = library.extra.get("novel_count", 0) + 1

            owner = sess.get_one(User, library.user_id)
            if extra.get("owner_name") != owner.name:
                extra["owner_name"] = owner.name

            library.extra = extra

            sess.commit()
            return True

    def remove_novel(self, library_id: str, user: User, novel_id: str) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)

            row = sess.exec(
                sa.delete(LibraryNovel).where(
                    sa.col(LibraryNovel.library_id) == library_id,
                    sa.col(LibraryNovel.novel_id) == novel_id,
                )
            )
            if row.rowcount == 0:
                return False

            extra = library.extra.copy()
            extra["novel_count"] = library.extra.get("novel_count", 0) - 1

            owner = sess.get_one(User, library.user_id)
            if extra.get("owner_name") != owner.name:
                extra["owner_name"] = owner.name

            library.extra = extra

            sess.commit()
            return True
