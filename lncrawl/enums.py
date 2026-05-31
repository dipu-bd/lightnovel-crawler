from enum import Enum, IntEnum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    LOCAL = "local"


class UserTier(IntEnum):
    BASIC = 0
    PREMIUM = 1
    VIP = 2


class JobType(IntEnum):
    NOVEL = 0
    NOVEL_BATCH = 1
    NOVEL_TRANSLATION = 2
    NOVEL_TRANSLATION_BATCH = 3
    FULL_NOVEL = 5
    FULL_NOVEL_BATCH = 6
    FULL_NOVEL_TRANSLATION = 7
    FULL_NOVEL_TRANSLATION_BATCH = 8
    CHAPTER = 10
    CHAPTER_BATCH = 11
    CHAPTER_TRANSLATION = 12
    CHAPTER_TRANSLATION_BATCH = 13
    VOLUME = 20
    VOLUME_BATCH = 21
    VOLUME_TRANSLATION = 22
    VOLUME_TRANSLATION_BATCH = 23
    IMAGE = 30
    IMAGE_BATCH = 31
    ARTIFACT = 40
    ARTIFACT_BATCH = 41


class JobStatus(IntEnum):
    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3
    CANCELED = 4


class JobPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class OutputFormat(str, Enum):
    json = "json"
    epub = "epub"
    text = "txt"
    pdf = "pdf"
    mobi = "mobi"
    docx = "docx"
    rtf = "rtf"
    fb2 = "fb2"
    azw3 = "azw3"
    lit = "lit"
    lrf = "lrf"
    pdb = "pdb"
    rb = "rb"
    tcr = "tcr"

    def __str__(self) -> str:
        return self.value


class NotificationItem(IntEnum):
    JOB_RUNNING = 10
    JOB_SUCCESS = 20
    JOB_FAILURE = 30
    JOB_CANCELED = 40
    NOVEL_SUCCESS = 50
    ARTIFACT_SUCCESS = 60


class FeedbackType(IntEnum):
    GENERAL = 0
    ISSUE = 1
    FEATURE = 2


class FeedbackStatus(IntEnum):
    PENDING = 0
    ACCEPTED = 1
    RESOLVED = 2


class ActivityType(IntEnum):
    LIBRARY = 1
    NOVEL = 2
    NOVEL_TRANSLATION = 3
    VOLUME = 4
    VOLUME_TRANSLATION = 5
    CHAPTER = 6
    CHAPTER_TRANSLATION = 7
    ACCOUNT = 8
    SOURCES = 9
    REQUEST = 10
    DOWNLOAD = 11


class LanguageCode(str, Enum):
    arabic = "ar"
    bangla = "bn"
    chinese = "zh"
    chinese_simplified = "zh-cn"
    chinese_traditional = "zh-tw"
    english = "en"
    french = "fr"
    german = "de"
    hindi = "hi"
    indonesian = "id"
    japanese = "ja"
    korean = "ko"
    portuguese = "pt"
    russian = "ru"
    spanish = "es"
    thai = "th"
    turkish = "tr"
    urdu = "ur"
    vietnamese = "vi"
