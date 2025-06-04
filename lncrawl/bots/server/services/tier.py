from lncrawl.models import OutputFormat

from ..models.job import JobPriority
from ..models.user import UserTier

##
# For Job creation
##

JOB_PRIORITY_LEVEL = {
    UserTier.BASIC: JobPriority.LOW,
    UserTier.PREMIUM: JobPriority.NORMAL,
    UserTier.VIP: JobPriority.HIGH,
}

##
# For JobRunner service
##
ENABLED_FORMATS = {
    UserTier.BASIC: [
        OutputFormat.json,
        OutputFormat.epub,
    ],
    UserTier.PREMIUM: [
        OutputFormat.json,
        OutputFormat.epub,
        OutputFormat.text,
        OutputFormat.web,
        OutputFormat.pdf,
    ],
    UserTier.VIP: list(OutputFormat),
}

SLOT_TIMEOUT_IN_SECOND = {
    UserTier.BASIC: 60,
    UserTier.PREMIUM: 5 * 60,
    UserTier.VIP: 2 * 60 * 60,
}
