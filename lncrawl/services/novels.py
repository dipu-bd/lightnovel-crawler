import shutil
from typing import Any, Dict, List, Optional

import sqlmodel as sq

from ..context import ctx
from ..dao import (
    Artifact,
    ChapterTranslation,
    LanguageCode,
    Novel,
    NovelGlossary,
    NovelSort,
    NovelTag,
    NovelTranslation,
    VolumeTranslation,
)
from ..exceptions import ServerErrors
from ..server.models import Paginated


class NovelService:
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
                # Match all selected tags via the indexed association table.
                wanted = sorted(set(tags))
                tag_match = (
                    sq.select(NovelTag.novel_id)
                    .where(sq.col(NovelTag.tag_name).in_(wanted))
                    .group_by(NovelTag.novel_id)
                    .having(sq.func.count(sq.col(NovelTag.tag_name)) == len(wanted))
                )
                conditions.append(sq.col(Novel.id).in_(tag_match))

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
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(NovelTag.tag_name, sq.func.count())
                .group_by(NovelTag.tag_name)
                .order_by(
                    sq.desc(sq.func.count()),
                    sq.asc(NovelTag.tag_name),
                )
            ).all()
        return {name: count for name, count in rows}

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

    def list_glossaries(
        self,
        novel_id: str,
        language: Optional[LanguageCode] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Map of glossary terms for a novel, keyed by language."""
        with ctx.db.session() as sess:
            stmt = sq.select(NovelGlossary).where(sq.col(NovelGlossary.novel_id) == novel_id)
            if language:
                stmt = stmt.where(sq.col(NovelGlossary.language) == language.value)
            rows = sess.exec(stmt).all()
            return {row.language: dict(row.terms) for row in rows}

    def update_glossary(
        self,
        novel_id: str,
        language: LanguageCode,
        terms: Dict[str, str],
    ) -> Dict[str, str]:
        """Replace the glossary terms of a novel for one target language."""
        cleaned = {
            key.strip(): value.strip()
            for key, value in terms.items()
            if key.strip() and value.strip()
        }
        with ctx.db.session() as sess:
            if not sess.get(Novel, novel_id):
                raise ServerErrors.no_such_novel
            row = sess.exec(
                sq.select(NovelGlossary)
                .where(
                    sq.col(NovelGlossary.novel_id) == novel_id,
                    sq.col(NovelGlossary.language) == language.value,
                )
                .limit(1)
            ).first()
            if row:
                row.terms = cleaned
                sess.add(row)
            elif cleaned:
                sess.add(
                    NovelGlossary(
                        novel_id=novel_id,
                        language=language.value,
                        terms=cleaned,
                    )
                )
            sess.commit()
        return cleaned

    def delete(self, novel_id: str, language: Optional[LanguageCode] = None) -> bool:
        if language:
            return self.delete_translation(novel_id, language)
        novel_dir = ctx.files.resolve(f"novels/{novel_id}")
        shutil.rmtree(novel_dir, True)
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                return True
            sess.exec(
                sq.delete(NovelTag).where(
                    sq.col(NovelTag.novel_id) == novel_id,
                )
            )
            sess.delete(novel)
            sess.commit()
        ctx.recommendations.invalidate(novel_id)
        ctx.recommendations.index_remove(novel_id)
        return True

    def delete_translation(self, novel_id: str, language: LanguageCode) -> bool:
        """Remove one target language of a novel: translation rows, glossary,
        translated chapter files, and artifacts in that language."""
        lang = language.value
        with ctx.db.session() as sess:
            chapters = sess.exec(
                sq.select(ChapterTranslation).where(
                    sq.col(ChapterTranslation.novel_id) == novel_id,
                    sq.col(ChapterTranslation.language) == lang,
                )
            ).all()
            for chapter in chapters:
                ctx.files.resolve(chapter.content_file).unlink(True)

            artifacts = sess.exec(
                sq.select(Artifact).where(
                    sq.col(Artifact.novel_id) == novel_id,
                    sq.col(Artifact.language) == lang,
                )
            ).all()
            for artifact in artifacts:
                ctx.files.resolve(artifact.output_file).unlink(True)
                sess.delete(artifact)

            for model in (ChapterTranslation, VolumeTranslation, NovelTranslation):
                sess.exec(
                    sq.delete(model).where(
                        sq.col(model.novel_id) == novel_id,
                        sq.col(model.language) == lang,
                    )
                )
            sess.commit()
        return True

    def find_by_url(self, novel_url: str) -> Optional[Novel]:
        with ctx.db.session() as sess:
            return sess.exec(sq.select(Novel).where(Novel.url == novel_url)).first()
