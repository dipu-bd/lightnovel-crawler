from typing import List, Optional

import sqlmodel as sq

from ..context import ctx
from ..dao import Library, LibraryFavorite, LibraryNovel, Novel, User, UserRole
from ..exceptions import ServerErrors
from ..server.models import LibraryItem, Paginated


class LibraryService:
    def __init__(self) -> None:
        pass

    def _ensure_owner(self, library: Library, user: User):
        if library.user_id != user.id and user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden

    def _ensure_visible(self, library: Library, user: User):
        if library.is_public or library.user_id == user.id or user.role == UserRole.ADMIN:
            return
        raise ServerErrors.forbidden

    def _get_library(self, sess: sq.Session, library_id: str) -> Library:
        library = sess.get(Library, library_id)
        if not library:
            raise ServerErrors.no_such_library
        return library

    def _get_library_cover(self, sess: sq.Session, library_id: str) -> Optional[str]:
        novels = sess.exec(
            sq.select(Novel)
            .join(LibraryNovel, sq.col(LibraryNovel.novel_id) == sq.col(Novel.id))
            .where(LibraryNovel.library_id == library_id)
            .order_by(sq.desc(Novel.updated_at))
        )
        for novel in novels:
            if novel.cover_available:
                return novel.cover_file

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
            stmt = sq.select(Library)
            cnt = sq.select(sq.func.count()).select_from(Library)

            if user_id:
                stmt = stmt.where(Library.user_id == user_id)
                cnt = cnt.where(Library.user_id == user_id)

            if public_only:
                stmt = stmt.where(sq.col(Library.is_public).is_(True))
                cnt = cnt.where(sq.col(Library.is_public).is_(True))

            if query:
                q = f"%{query.lower()}%"
                stmt = stmt.where(sq.col(Library.name).ilike(q))
                cnt = cnt.where(sq.col(Library.name).ilike(q))

            stmt = stmt.order_by(sq.desc(Library.updated_at))

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

    def list_favorites(
        self,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
        *,
        query: str = "",
    ) -> Paginated[Library]:
        """List libraries the user has favorited (only ones still public)."""
        with ctx.db.session() as sess:
            join_on = sq.col(LibraryFavorite.library_id) == sq.col(Library.id)
            where = [
                LibraryFavorite.user_id == user_id,
                sq.col(Library.is_public).is_(True),
            ]
            if query:
                where.append(sq.col(Library.name).ilike(f"%{query.lower()}%"))

            stmt = (
                sq.select(Library)
                .join(LibraryFavorite, join_on)
                .where(*where)
                .order_by(sq.desc(LibraryFavorite.created_at))
                .offset(offset)
                .limit(limit)
            )
            cnt = (
                sq.select(sq.func.count())
                .select_from(LibraryFavorite)
                .join(Library, join_on)
                .where(*where)
            )

            items = sess.exec(stmt).all()
            total = sess.exec(cnt).one()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def list_favorite_ids(self, user_id: str) -> List[str]:
        """Return the ids of all libraries the user has favorited."""
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(LibraryFavorite.library_id).where(LibraryFavorite.user_id == user_id)
            ).all()
            return list(rows)

    def list_all(
        self,
        user_id: Optional[str] = None,
    ) -> List[LibraryItem]:
        with ctx.db.session() as sess:
            stmt = sq.select(Library)
            if user_id:
                stmt = stmt.where(Library.user_id == user_id)
            stmt = stmt.order_by(sq.desc(Library.updated_at))
            libraries = sess.exec(stmt).all()

            return [
                LibraryItem(
                    id=library.id,
                    name=library.name,
                    is_public=library.is_public,
                    cover_file=library.cover_file,
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
            limit = ctx.tier.max_libraries(user)
            if limit is not None:
                count = sess.scalar(
                    sq.select(sq.func.count())
                    .select_from(Library)
                    .where(Library.user_id == user.id)
                )
                if count and count >= limit:
                    raise ServerErrors.library_limit_reached

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

            modified = False
            extra = library.extra.copy()

            owner = sess.get_one(User, library.user_id)
            if library.extra.get("owner_name") != owner.name:
                extra["owner_name"] = owner.name
                modified = True

            if "novel_cover" not in library.extra:
                extra["novel_cover"] = self._get_library_cover(sess, library_id)
                modified = True

            if modified:
                library.extra = extra
                sess.commit()

            return library

    def add_favorite(self, user: User, library_id: str) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_visible(library, user)

            existing = sess.get(LibraryFavorite, (user.id, library_id))
            if existing:
                return True

            sess.add(LibraryFavorite(user_id=user.id, library_id=library_id))
            sess.commit()
            return True

    def remove_favorite(self, user: User, library_id: str) -> bool:
        with ctx.db.session() as sess:
            row = sess.exec(
                sq.delete(LibraryFavorite).where(
                    sq.col(LibraryFavorite.user_id) == user.id,
                    sq.col(LibraryFavorite.library_id) == library_id,
                )
            )
            sess.commit()
            return row.rowcount > 0

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
                sq.select(sq.func.count())
                .select_from(LibraryNovel)
                .where(LibraryNovel.library_id == library_id)
            )
            stmt = (
                sq.select(Novel)
                .join(LibraryNovel, sq.col(LibraryNovel.novel_id) == sq.col(Novel.id))
                .where(LibraryNovel.library_id == library_id)
                .order_by(sq.desc(Novel.updated_at))
                .offset(offset)
                .limit(limit)
            )

            total = sess.exec(cnt).one()
            items = sess.exec(stmt).all()

            modified = False
            extra = library.extra.copy()

            if library.extra.get("novel_count") != total:
                extra = library.extra.copy()
                extra["novel_count"] = total
                modified = True

            if "novel_cover" not in library.extra:
                for novel in items:
                    if novel.cover_available:
                        extra["novel_cover"] = novel.cover_file
                        modified = True
                        break

            if modified:
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

            limit = ctx.tier.max_novels_per_library(user)
            if limit is not None and library.extra.get("novel_count", 0) >= limit:
                raise ServerErrors.novel_limit_reached

            existing = sess.scalar(
                sq.select(LibraryNovel).where(
                    LibraryNovel.library_id == library_id,
                    LibraryNovel.novel_id == novel_id,
                )
            )
            if existing:
                return True

            link = LibraryNovel(library_id=library_id, novel_id=novel_id)
            sess.add(link)

            extra = library.extra.copy()

            owner = sess.get_one(User, library.user_id)
            if extra.get("owner_name") != owner.name:
                extra["owner_name"] = owner.name

            extra["novel_count"] = library.extra.get("novel_count", 0) + 1
            if not library.cover_available and novel.cover_available:
                extra["novel_cover"] = novel.cover_file

            library.extra = extra

            sess.commit()
            return True

    def remove_novel(self, library_id: str, user: User, novel_id: str) -> bool:
        with ctx.db.session() as sess:
            library = self._get_library(sess, library_id)
            self._ensure_owner(library, user)

            row = sess.exec(
                sq.delete(LibraryNovel).where(
                    sq.col(LibraryNovel.library_id) == library_id,
                    sq.col(LibraryNovel.novel_id) == novel_id,
                )
            )
            if row.rowcount == 0:
                return False

            extra = library.extra.copy()
            extra["novel_count"] = library.extra.get("novel_count", 0) - 1

            if not library.cover_file or novel_id in library.cover_file:
                extra["novel_cover"] = self._get_library_cover(sess, library_id)

            owner = sess.get_one(User, library.user_id)
            if extra.get("owner_name") != owner.name:
                extra["owner_name"] = owner.name

            library.extra = extra

            sess.commit()
            return True
