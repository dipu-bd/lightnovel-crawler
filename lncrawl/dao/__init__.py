from typing import List, Type

from sqlalchemy import Table
from sqlmodel import SQLModel

from ..enums import *  # noqa: F401,F403
from .activity import UserActivity
from .announcement import Announcement
from .artifact import Artifact
from .chapter import Chapter, ChapterTranslation
from .chapter_image import ChapterImage
from .job import Job
from .library import Library, LibraryFavorite, LibraryNovel
from .novel import Novel, NovelGlossary, NovelTranslation
from .read_history import ReadHistory
from .secrets import Secret
from .tag import NovelTag, Tag
from .user import User, UserToken
from .volume import Volume, VolumeTranslation

models: List[Type[SQLModel]] = [
    UserActivity,
    User,
    UserToken,
    Tag,
    NovelTag,
    Library,
    LibraryNovel,
    LibraryFavorite,
    Novel,
    NovelTranslation,
    NovelGlossary,
    Volume,
    VolumeTranslation,
    Chapter,
    ChapterTranslation,
    ChapterImage,
    ReadHistory,
    Artifact,
    Job,
    Secret,
    Announcement,
]

tables: List[Table] = [
    getattr(model, "__table__") for model in models if hasattr(model, "__table__")
]
