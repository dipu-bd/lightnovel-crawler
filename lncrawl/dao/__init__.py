from typing import List, Type

from sqlalchemy import Table
from sqlmodel import SQLModel

from ..enums import *  # noqa: F401,F403
from .activity import UserActivity
from .announcement import Announcement
from .artifact import Artifact
from .chapter import Chapter, ChapterTranslation
from .chapter_image import ChapterImage
from .feedback import Feedback
from .job import Job
from .library import Library, LibraryNovel
from .novel import Novel, NovelTranslation
from .read_history import ReadHistory
from .secrets import Secret
from .tag import Tag
from .user import User, UserToken
from .volume import Volume, VolumeTranslation

models: List[Type[SQLModel]] = [
    UserActivity,
    User,
    UserToken,
    Tag,
    Library,
    LibraryNovel,
    Novel,
    NovelTranslation,
    Volume,
    VolumeTranslation,
    Chapter,
    ChapterTranslation,
    ChapterImage,
    ReadHistory,
    Artifact,
    Job,
    Secret,
    Feedback,
    Announcement,
]

tables: List[Table] = [
    getattr(model, "__table__") for model in models if hasattr(model, "__table__")
]
