from fastapi import APIRouter, Body, Security

from ...context import ctx
from ...dao import NotificationItem, User
from ...server.models import PutNotificationRequest, UpdateRequest
from ..security import ensure_user

# The root router
router = APIRouter()


@router.put(
    "/notifications",
    summary="Save user notification settings",
)
def put_notification_settings(
    user: User = Security(ensure_user), body: PutNotificationRequest = Body()
) -> bool:
    request = UpdateRequest(
        extra=dict(
            email_alerts={
                NotificationItem(int(k)): 1 if v else 0
                for k, v in body.email_alerts.items()
                if v and int(k) in list(NotificationItem)
            }
        )
    )
    ctx.users.update(user.id, request)
    return True
