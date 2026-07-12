from collections import Counter
import shutil
from typing import Any, Dict, List, Optional

import sqlmodel as sq

from ..context import ctx
from ..dao import LanguageCode, Novel, NovelSort, NovelTranslation
from ..exceptions import ServerErrors
from ..server.models import Paginated
from ..utils.time_utils import current_timestamp

# Tag vocabulary is derived by scanning all novels, so cache it briefly.
_TAGS_CACHE_TTL = 5 * 60 * 1000


class NovelService:
    def __init__(self) -> None:
        self._tags_cache: Optional[Dict[str, int]] = None
        self._tags_cache_at: int = 0

    def list(
        self,
        search: str = "",
        offset: int = 0,
        limit: int = 20,
        domain: str = "",
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        manga: Optional[bool] = None,
        mtl: Optional[bool] = None,
        min_chapters: int = 0,
        sort: NovelSort = NovelSort.updated,
    ) -> Paginated[Novel]:
        with ctx.db.session() as sess:
            stmt = sq.select(Novel)
            cnt = sq.select(sq.func.count()).select_from(Novel)

            # Apply filters
            conditions: List[Any] = []

            if domain:
                conditions.append(sq.col(Novel.url).ilike(f"%{domain}%"))

            if search:
                conditions.append(
                    sq.or_(
                        sq.col(Novel.title).ilike(f"%{search}%"),
                        sq.col(Novel.authors).ilike(f"%{search}%"),
                        sq.col(Novel.synopsis).ilike(f"%{search}%"),
                    )
                )

            if language:
                conditions.append(sq.col(Novel.language) == language)

            if manga is not None:
                conditions.append(sq.col(Novel.manga).is_(manga))
            if mtl is not None:
                conditions.append(sq.col(Novel.mtl).is_(mtl))

            if min_chapters > 0:
                conditions.append(sq.col(Novel.chapter_count) >= min_chapters)

            if tags:
                # Match all selected tags. Tags are a JSON array of strings;
                # cast to text and match the quoted token for SQLite/Postgres
                # portability (the quotes keep "Action" from hitting "Action X").
                tags_text = sq.cast(sq.col(Novel.tags), sq.String)
                for tag in tags:
                    conditions.append(tags_text.ilike(f'%"{tag}"%'))

            if conditions:
                cnd = sq.and_(*conditions)
                stmt = stmt.where(cnd)
                cnt = cnt.where(cnd)

            # Apply sorting
            if sort == NovelSort.popular:
                stmt = stmt.order_by(
                    sq.desc(Novel.popularity),
                    sq.desc(Novel.updated_at),
                )
            elif sort == NovelSort.created:
                stmt = stmt.order_by(sq.desc(Novel.created_at))
            elif sort == NovelSort.chapters:
                stmt = stmt.order_by(sq.desc(Novel.chapter_count))
            elif sort == NovelSort.title_asc:
                stmt = stmt.order_by(sq.asc(Novel.title))
            elif sort == NovelSort.title_desc:
                stmt = stmt.order_by(sq.desc(Novel.title))
            else:
                stmt = stmt.order_by(sq.desc(Novel.updated_at))

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

    def list_tags(self) -> Dict[str, int]:
        now = current_timestamp()
        if self._tags_cache is not None and now - self._tags_cache_at < _TAGS_CACHE_TTL:
            return self._tags_cache
        counter: Counter[str] = Counter()
        with ctx.db.session() as sess:
            for tags in sess.exec(sq.select(Novel.tags)).all():
                for tag in tags or []:
                    if tag:
                        counter[tag] += 1
        result = dict(counter.most_common())
        self._tags_cache = result
        self._tags_cache_at = now
        return result

    def list_domains(self) -> Dict[str, int]:
        with ctx.db.session() as sess:
            domains = sess.exec(
                sq.select(
                    Novel.domain,
                    sq.func.count(sq.col(Novel.id)).label("total_novels"),
                ).group_by(Novel.domain)
            ).all()
        return {domain: total_novels for domain, total_novels in domains}

    def get(self, novel_id: str, language: Optional[LanguageCode] = None) -> Novel:
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise ServerErrors.no_such_novel
        if language:
            translation = self.get_novel_translation(novel, language)
            if not translation:
                raise ServerErrors.no_such_novel.with_extra(language)
            novel.title = translation.title
            novel.authors = translation.authors
            novel.synopsis = translation.synopsis
        return novel

    def list_translation_languages(self, novel_id: str) -> List[LanguageCode]:
        with ctx.db.session() as sess:
            translations = sess.exec(
                sq.select(NovelTranslation.language).where(
                    NovelTranslation.novel_id == novel_id,
                )
            ).all()
            return [LanguageCode(lang) for lang in translations]

    def get_novel_translation(self, novel: Novel, language: LanguageCode):
        with ctx.db.session() as sess:
            return sess.exec(
                sq.select(NovelTranslation)
                .where(
                    NovelTranslation.novel_id == novel.id,
                    NovelTranslation.language == language,
                )
                .limit(1)
            ).first()

    def delete(self, novel_id: str) -> bool:
        novel_dir = ctx.files.resolve(f"novels/{novel_id}")
        shutil.rmtree(novel_dir, True)
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                return True
            sess.delete(novel)
            sess.commit()
        ctx.recommendations.invalidate(novel_id)
        ctx.recommendations.index_remove(novel_id)
        return True

    def find_by_url(self, novel_url: str) -> Optional[Novel]:
        with ctx.db.session() as sess:
            return sess.exec(sq.select(Novel).where(Novel.url == novel_url)).first()
