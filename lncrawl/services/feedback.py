from typing import Any, Dict, List, Optional

import sqlmodel as sa

from ..context import ctx
from ..dao import Feedback, FeedbackStatus, FeedbackType, User
from ..enums import UserRole
from ..exceptions import ServerErrors
from ..server.models import Paginated


class FeedbackService:
    def __init__(self) -> None:
        pass

    def create(
        self,
        user: User,
        *,
        type: FeedbackType,
        subject: str,
        message: str,
        extra: Dict[str, Any],
    ) -> Feedback:
        extra.update({"user_name": user.name})
        with ctx.db.session() as sess:
            feedback = Feedback(
                user_id=user.id,
                type=type,
                subject=subject,
                message=message,
                status=FeedbackStatus.PENDING,
                extra=extra,
            )
            sess.add(feedback)
            sess.commit()
            return feedback

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        *,
        search: str = "",
        user_id: Optional[str] = None,
        status: Optional[FeedbackStatus] = None,
        type: Optional[FeedbackType] = None,
    ) -> Paginated[Feedback]:
        with ctx.db.session() as sess:
            stmt = sa.select(Feedback)
            cnt = sa.select(sa.func.count()).select_from(Feedback)

            # Apply filters
            conditions: List[Any] = []

            if search:
                q = f"%{search}%"
                conditions.append(
                    sa.or_(
                        sa.col(Feedback.subject).ilike(q),
                        sa.col(Feedback.message).ilike(q),
                    )
                )

            if status is not None:
                conditions.append(Feedback.status == status)

            if type is not None:
                conditions.append(Feedback.type == type)

            if user_id is not None:
                conditions.append(Feedback.user_id == user_id)

            if conditions:
                stmt = stmt.where(*conditions)
                cnt = cnt.where(*conditions)

            # Apply sorting
            stmt = stmt.order_by(sa.desc(Feedback.created_at))

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

    def get(self, feedback_id: str) -> Feedback:
        with ctx.db.session() as sess:
            feedback = sess.get(Feedback, feedback_id)
            if not feedback:
                raise ServerErrors.not_found

            # Ensure user_name is in extra
            user = sess.get_one(User, feedback.user_id)
            if feedback.extra.get("user_name") != user.name:
                extra = feedback.extra.copy()
                extra["user_name"] = user.name
                feedback.extra = extra
                sess.commit()

            return feedback

    def update(
        self,
        user: User,
        feedback_id: str,
        *,
        subject: Optional[str] = None,
        message: Optional[str] = None,
        type: Optional[FeedbackType] = None,
    ) -> Feedback:
        with ctx.db.session() as sess:
            feedback = sess.get(Feedback, feedback_id)
            if not feedback:
                raise ServerErrors.not_found

            if feedback.user_id != user.id:
                raise ServerErrors.forbidden

            if type is not None:
                feedback.type = type
            if subject is not None:
                feedback.subject = subject
            if message is not None:
                feedback.message = message

            sess.commit()
            sess.refresh(feedback)
            return feedback

    def respond(
        self,
        user: User,
        feedback_id: str,
        *,
        admin_notes: str,
        status: FeedbackStatus,
    ) -> Feedback:
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden

        with ctx.db.session() as sess:
            feedback = sess.get(Feedback, feedback_id)
            if not feedback:
                raise ServerErrors.not_found

            feedback.status = status
            feedback.admin_notes = admin_notes

            sess.commit()
            sess.refresh(feedback)
            return feedback

    def delete(self, user: User, feedback_id: str) -> bool:
        with ctx.db.session() as sess:
            feedback = sess.get(Feedback, feedback_id)
            if not feedback:
                return True
            if user.role != UserRole.ADMIN and feedback.user_id != user.id:
                raise ServerErrors.forbidden
            sess.delete(feedback)
            sess.commit()
            return True
