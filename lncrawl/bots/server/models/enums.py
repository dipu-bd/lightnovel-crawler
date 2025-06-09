from enum import Enum, IntEnum

from lncrawl.models import OutputFormat

__all__ = [
    'OutputFormat',
    'UserRole',
    'UserTier',
    'JobStatus',
    'JobPriority',
    'RunState',
]


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserTier(IntEnum):
    BASIC = 0
    PREMIUM = 1
    VIP = 2


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "done"


class JobPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class RunState(IntEnum):
    FAILED = 0
    SUCCESS = 1
    CANCELED = 2
    FETCHING_NOVEL = 3
    FETCHING_CONTENT = 4
    CREATING_ARTIFACTS = 5
