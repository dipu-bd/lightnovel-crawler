from typing import List, Optional

import sqlmodel as sq

from ..context import ctx
from ..core.taskman import TaskManager
from ..dao import ActivityType, Novel, UserActivity
from ..server.models.activity import (
    DailyActiveUsers,
    DailyTypeCount,
    EngagementBucket,
    GlobalActivitySummary,
    HourlyActivityCell,
    TopNovelActivity,
    TopUserActivity,
    UserActivityStats,
)
from ..utils.time_utils import current_timestamp


class UserActivityService:
    def __init__(self) -> None:
        self.taskman = TaskManager(ctx.config.crawler.runner_concurrency)

    def record(self, user_id: str, activity_type: ActivityType, target_id: str) -> None:
        self.taskman.submit_task(self._record, user_id, activity_type, target_id)

    def _record(self, user_id: str, activity_type: ActivityType, target_id: str) -> None:
        ts = current_timestamp()
        with ctx.db.session() as sess:
            activity = sess.get(UserActivity, (user_id, activity_type, target_id))
            if activity is None:
                activity = UserActivity(
                    user_id=user_id,
                    activity_type=activity_type,
                    target_id=target_id,
                    updated_at=ts,
                )
                sess.add(activity)
            else:
                activity.visit_count += 1
                activity.updated_at = ts

            # Keep a live, retention-independent popularity counter on the novel
            # so the novel list can sort by it without touching this table.
            # A Core UPDATE avoids the BaseTable before_update hook (so it does
            # not bump updated_at) and increments atomically.
            if activity_type in (ActivityType.NOVEL, ActivityType.NOVEL_TRANSLATION):
                sess.exec(
                    sq.update(Novel)
                    .where(sq.col(Novel.id) == target_id)
                    .values(popularity=sq.col(Novel.popularity) + 1)
                )

            sess.commit()

    def get_visit_count(self, target_id: str, activity_type: ActivityType) -> int:
        with ctx.db.session() as sess:
            stmt = sq.select(
                sq.func.coalesce(sq.func.sum(UserActivity.visit_count), 0),
            ).where(
                UserActivity.target_id == target_id,
                sq.col(UserActivity.activity_type) == activity_type,
            )
            return sess.exec(stmt).one_or_none() or 0

    def get_user_last_activity(self, user_id: str) -> Optional[int]:
        with ctx.db.session() as sess:
            stmt = sq.select(
                sq.func.max(UserActivity.updated_at),
            ).where(
                UserActivity.user_id == user_id,
            )
            return sess.exec(stmt).one_or_none()

    def get_user_activity_count(self, user_id: str) -> int:
        with ctx.db.session() as sess:
            stmt = sq.select(
                sq.func.coalesce(sq.func.sum(UserActivity.visit_count), 0),
            ).where(
                UserActivity.user_id == user_id,
            )
            return sess.exec(stmt).one_or_none() or 0

    def get_user_stats(self, user_id: str) -> UserActivityStats:
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(
                    sq.col(UserActivity.activity_type),
                    sq.func.sum(UserActivity.visit_count),
                    sq.func.max(UserActivity.updated_at),
                )
                .where(UserActivity.user_id == user_id)
                .group_by(sq.col(UserActivity.activity_type))
            ).all()

        visits = {ActivityType(int(r[0])): int(r[1]) for r in rows}
        last_activity = max((int(r[2]) for r in rows), default=None)
        activity_count = sum(int(r[1]) for r in rows)

        return UserActivityStats(
            last_activity=last_activity,
            activity_count=activity_count,
            visits=visits,
        )

    def _cutoff(self, days: int) -> int:
        return current_timestamp() - days * 86_400_000

    def _day_label(self, col):
        """Return an SQL expression that truncates a millisecond-epoch column to YYYY-MM-DD."""
        if ctx.db.engine.dialect.name == "postgresql":
            return sq.func.to_char(sq.func.to_timestamp(col / sq.literal(1000.0)), "YYYY-MM-DD")
        return sq.func.strftime("%Y-%m-%d", sq.func.datetime(col / 1000, "unixepoch"))

    def get_admin_summary(self, days: int) -> GlobalActivitySummary:
        """Global totals: active users + event counts broken down by type."""
        cutoff = self._cutoff(days)
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(
                    sq.col(UserActivity.activity_type),
                    sq.func.count(sq.distinct(UserActivity.user_id)),
                    sq.func.sum(UserActivity.visit_count),
                )
                .where(UserActivity.updated_at >= cutoff)
                .group_by(sq.col(UserActivity.activity_type))
            ).all()
            active_users = sess.exec(
                sq.select(sq.func.count(sq.distinct(UserActivity.user_id))).where(
                    UserActivity.updated_at >= cutoff
                )
            ).one()
            dau = sess.exec(
                sq.select(sq.func.count(sq.distinct(UserActivity.user_id))).where(
                    UserActivity.updated_at >= self._cutoff(1)
                )
            ).one()
            mau = sess.exec(
                sq.select(sq.func.count(sq.distinct(UserActivity.user_id))).where(
                    UserActivity.updated_at >= self._cutoff(30)
                )
            ).one()
            # Users whose earliest activity (min created_at) falls within the window.
            first_seen = (
                sq.select(sq.func.min(UserActivity.created_at).label("first"))
                .group_by(UserActivity.user_id)
                .subquery()
            )
            new_users = sess.exec(
                sq.select(sq.func.count())
                .select_from(first_seen)
                .where(first_seen.c.first >= cutoff)
            ).one()
        by_type = {ActivityType(int(r[0])): int(r[2]) for r in rows}
        total_events = sum(int(r[2]) for r in rows)
        total_users = ctx.users.count()
        return GlobalActivitySummary(
            total_users=total_users,
            active_users=active_users,
            total_events=total_events,
            by_type=by_type,
            dau=int(dau),
            mau=int(mau),
            new_users=int(new_users),
        )

    def get_admin_dau(self, days: int) -> List[DailyActiveUsers]:
        """Distinct active users per calendar day."""
        cutoff = self._cutoff(days)
        day = self._day_label(UserActivity.updated_at).label("day")
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(day, sq.func.count(sq.distinct(UserActivity.user_id)))
                .where(UserActivity.updated_at >= cutoff)
                .group_by(day)
                .order_by(day)
            ).all()
        return [DailyActiveUsers(date=r[0], users=int(r[1])) for r in rows]

    def get_admin_type_trend(self, days: int) -> List[DailyTypeCount]:
        """Row count per (day, activity_type) for the multi-series line chart."""
        cutoff = self._cutoff(days)
        day = self._day_label(UserActivity.updated_at).label("day")
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(day, sq.col(UserActivity.activity_type), sq.func.count())
                .where(UserActivity.updated_at >= cutoff)
                .group_by(day, sq.col(UserActivity.activity_type))
                .order_by(day)
            ).all()
        return [
            DailyTypeCount(date=r[0], activity_type=ActivityType(int(r[1])), events=int(r[2]))
            for r in rows
        ]

    def get_admin_hourly_heatmap(
        self, days: int, tz_offset_minutes: int = 0
    ) -> List[HourlyActivityCell]:
        """Activity volume bucketed by day-of-week x hour-of-day.

        Buckets are derived from each record's ``updated_at`` (the last-touched
        time), so this is a proxy for *when* users are active rather than a true
        event log. Useful for spotting low-traffic windows for deployments.

        The day/hour split is computed with portable integer epoch arithmetic so
        it behaves identically on SQLite and PostgreSQL. Floor division (``//``)
        keeps the buckets integer; SQLAlchemy's ``/`` is true division and yields
        floats, which would put every record in its own bucket and defeat the
        GROUP BY. ``tz_offset_minutes`` is added to UTC before bucketing so the
        grid reflects the viewer's local time (matching JS
        ``-Date.getTimezoneOffset()``).
        """
        cutoff = self._cutoff(days)
        # seconds since epoch, shifted into the requested timezone
        secs = sq.col(UserActivity.updated_at) // sq.literal(1000) + sq.literal(
            tz_offset_minutes * 60
        )
        hour = ((secs // sq.literal(3600)) % sq.literal(24)).label("hour")
        # epoch day 0 (1970-01-01) was a Thursday; +4 aligns 0 to Sunday
        dow = (((secs // sq.literal(86400)) + sq.literal(4)) % sq.literal(7)).label("dow")
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(dow, hour, sq.func.count())
                .where(UserActivity.updated_at >= cutoff)
                .group_by(dow, hour)
            ).all()
        return [
            HourlyActivityCell(
                dow=int(r[0]),
                hour=int(r[1]),
                events=int(r[2]),
            )
            for r in rows
        ]

    def get_admin_top_novels(self, days: int, limit: int = 20) -> List[TopNovelActivity]:
        """Most-visited novels (original + translated reads), ranked by visits."""
        cutoff = self._cutoff(days)
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(
                    UserActivity.target_id,
                    sq.func.sum(UserActivity.visit_count),
                    sq.func.count(sq.distinct(UserActivity.user_id)),
                )
                .where(
                    UserActivity.updated_at >= cutoff,
                    sq.col(UserActivity.activity_type).in_(
                        [ActivityType.NOVEL, ActivityType.NOVEL_TRANSLATION]
                    ),
                )
                .group_by(UserActivity.target_id)
                .order_by(sq.func.sum(UserActivity.visit_count).desc())
                .limit(limit)
            ).all()
            # batch-load titles for the ranked novels in the same session
            novel_ids = [r[0] for r in rows]
            titles = {
                n.id: n.title
                for n in sess.exec(sq.select(Novel).where(sq.col(Novel.id).in_(novel_ids))).all()
            }
        return [
            TopNovelActivity(
                novel_id=r[0],
                title=titles.get(r[0], "(deleted)"),
                visits=int(r[1]),
                readers=int(r[2]),
            )
            for r in rows
        ]

    def get_admin_engagement(self, days: int) -> List[EngagementBucket]:
        """Distribution of active users by how many events they generated."""
        cutoff = self._cutoff(days)
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(sq.func.sum(UserActivity.visit_count))
                .where(UserActivity.updated_at >= cutoff)
                .group_by(UserActivity.user_id)
            ).all()
        labels = ["1", "2-5", "6-20", "21-50", "50+"]
        counts = {label: 0 for label in labels}
        for row in rows:
            events = int(row if not isinstance(row, tuple) else row[0])
            if events <= 1:
                counts["1"] += 1
            elif events <= 5:
                counts["2-5"] += 1
            elif events <= 20:
                counts["6-20"] += 1
            elif events <= 50:
                counts["21-50"] += 1
            else:
                counts["50+"] += 1
        return [EngagementBucket(bucket=label, users=counts[label]) for label in labels]

    def get_admin_top_users(self, days: int, limit: int = 20) -> List[TopUserActivity]:
        """Users ranked by total visit_count; enriched with name/email."""
        cutoff = self._cutoff(days)
        with ctx.db.session() as sess:
            rows = sess.exec(
                sq.select(
                    UserActivity.user_id,
                    sq.col(UserActivity.activity_type),
                    sq.func.sum(UserActivity.visit_count),
                )
                .where(UserActivity.updated_at >= cutoff)
                .group_by(UserActivity.user_id, sq.col(UserActivity.activity_type))
            ).all()
        # aggregate per-type rows into per-user totals in Python
        user_totals: dict = {}
        for user_id, atype, count in rows:
            entry = user_totals.setdefault(user_id, {"total": 0, "by_type": {}})
            entry["total"] += int(count)
            entry["by_type"][ActivityType(int(atype))] = int(count)
        top = sorted(user_totals.items(), key=lambda x: -x[1]["total"])[:limit]
        # batch-load user name/email for each top user
        result = []
        for user_id, data in top:
            user = ctx.users.get(user_id)
            if user:
                result.append(
                    TopUserActivity(
                        user_id=user_id,
                        username=user.name or "",
                        email=user.email,
                        total=data["total"],
                        by_type=data["by_type"],
                    )
                )
        return result
