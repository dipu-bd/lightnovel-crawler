from typing import Optional

from sqlalchemy.exc import IntegrityError
import sqlmodel as sq

from ..context import ctx
from ..core.taskman import TaskManager
from ..dao import ActivityType, UserActivity
from ..server.models.activity import UserActivityStats
from ..utils.time_utils import current_timestamp


class UserActivityService:
    def __init__(self) -> None:
        self.taskman = TaskManager(3)

    def record(self, user_id: str, activity_type: ActivityType, target_id: str) -> None:
        self.taskman.submit_task(self._record, user_id, activity_type, target_id)

    def _record(self, user_id: str, activity_type: ActivityType, target_id: str) -> None:
        ts = current_timestamp()
        with ctx.db.session() as sess:
            try:
                sess.add(
                    UserActivity(
                        user_id=user_id,
                        activity_type=activity_type,
                        target_id=target_id,
                        updated_at=ts,
                    )
                )
                sess.commit()
            except IntegrityError:
                sess.rollback()
                sess.exec(
                    sq.update(UserActivity)
                    .where(
                        sq.col(UserActivity.user_id) == user_id,
                        sq.col(UserActivity.target_id) == target_id,
                        sq.col(UserActivity.activity_type) == activity_type,
                    )
                    .values(
                        visit_count=UserActivity.visit_count + 1,
                        last_visited_at=ts,
                    )
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
