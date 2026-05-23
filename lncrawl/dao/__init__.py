from typing import List, Type

from sqlalchemy import Table
from sqlmodel import SQLModel

from ..enums import *  # noqa: F401,F403
from .announcement import Announcement
from .artifact import Artifact
from .chapter import Chapter, ChapterTranslation
from .chapter_image import ChapterImage
from .feedback import Feedback
from .job import Job
from .library import Library, LibraryNovel
from .novel import Novel
from .read_history import ReadHistory
from .secrets import Secret
from .tag import Tag
from .user import User, UserToken
from .volume import Volume

models: List[Type[SQLModel]] = [
    User,
    UserToken,
    Tag,
    Library,
    LibraryNovel,
    Novel,
    Volume,
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
