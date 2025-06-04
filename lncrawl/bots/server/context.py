from functools import cached_property
from typing import Optional

from .utils.decorators import autoclose

_cache: Optional['ServerContext'] = None


class ServerContext:
    def __new__(cls):
        global _cache
        if _cache is None:
            _cache = super().__new__(cls)
        return _cache

    @cached_property
    def config(self):
        from .config import Config
        return Config()

    @cached_property
    @autoclose
    def db(self):
        from .db import DB
        return DB(self)

    @cached_property
    def users(self):
        from .services.users import UserService
        return UserService(self)

    @cached_property
    def jobs(self):
        from .services.jobs import JobService
        return JobService(self)

    @cached_property
    def novels(self):
        from .services.novels import NovelService
        return NovelService(self)

    @cached_property
    def artifacts(self):
        from .services.artifacts import ArtifactService
        return ArtifactService(self)

    @cached_property
    @autoclose
    def scheduler(self):
        from .services.scheduler import JobScheduler
        return JobScheduler(self)
