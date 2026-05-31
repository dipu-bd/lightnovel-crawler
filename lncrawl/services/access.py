from typing import FrozenSet, Optional

from ..dao import User
from ..enums import JobPriority, OutputFormat, UserTier


class AccessManager:
    _JOB_PRIORITY = {
        UserTier.BASIC: JobPriority.LOW,
        UserTier.PREMIUM: JobPriority.NORMAL,
        UserTier.VIP: JobPriority.HIGH,
    }
    _FULL_NOVEL_BATCH_ALLOWED = {
        UserTier.BASIC: True,
        UserTier.PREMIUM: True,
        UserTier.VIP: True,
    }
    _AUTO_FETCH_ENABLED = {
        UserTier.BASIC: False,
        UserTier.PREMIUM: False,
        UserTier.VIP: True,
    }
    _TRANSLATION_ENABLED = {
        UserTier.BASIC: False,
        UserTier.PREMIUM: True,
        UserTier.VIP: True,
    }
    # None = unlimited
    _MAX_ACTIVE_JOBS = {
        UserTier.BASIC: 5,
        UserTier.PREMIUM: 50,
        UserTier.VIP: None,
    }
    _MAX_LIBRARIES = {
        UserTier.BASIC: 10,
        UserTier.PREMIUM: 100,
        UserTier.VIP: None,
    }
    _MAX_NOVELS_PER_LIBRARY = {
        UserTier.BASIC: 25,
        UserTier.PREMIUM: 250,
        UserTier.VIP: None,
    }
    _MAX_READ_HISTORY = {
        UserTier.BASIC: 500,
        UserTier.PREMIUM: 5000,
        UserTier.VIP: 10000,
    }
    _ENABLED_FORMATS = {
        UserTier.BASIC: frozenset(
            [
                OutputFormat.json,
                OutputFormat.epub,
            ]
        ),
        UserTier.PREMIUM: frozenset(
            [
                OutputFormat.json,
                OutputFormat.epub,
                OutputFormat.text,
                OutputFormat.mobi,
                OutputFormat.docx,
                OutputFormat.fb2,
                OutputFormat.azw3,
                OutputFormat.lit,
                OutputFormat.pdb,
                OutputFormat.tcr,
            ]
        ),
        UserTier.VIP: frozenset(OutputFormat),
    }

    def job_priority(self, user: User) -> JobPriority:
        return self._JOB_PRIORITY[user.tier]

    def enabled_formats(self, user: User) -> FrozenSet[OutputFormat]:
        return self._ENABLED_FORMATS[user.tier]

    def full_novel_batch_allowed(self, user: User) -> bool:
        return self._FULL_NOVEL_BATCH_ALLOWED[user.tier]

    def auto_fetch_enabled(self, user: User) -> bool:
        return self._AUTO_FETCH_ENABLED[user.tier]

    def translation_enabled(self, user: User) -> bool:
        return self._TRANSLATION_ENABLED[user.tier]

    def max_active_jobs(self, user: User) -> Optional[int]:
        return self._MAX_ACTIVE_JOBS[user.tier]

    def max_libraries(self, user: User) -> Optional[int]:
        return self._MAX_LIBRARIES[user.tier]

    def max_novels_per_library(self, user: User) -> Optional[int]:
        return self._MAX_NOVELS_PER_LIBRARY[user.tier]

    def max_read_history(self, user: User) -> Optional[int]:
        return self._MAX_READ_HISTORY[user.tier]
