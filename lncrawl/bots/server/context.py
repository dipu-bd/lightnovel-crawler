from functools import cached_property
from typing import Optional

from lncrawl.core.sources import load_sources

_cache: Optional['ServerContext'] = None


class ServerContext:
    def __new__(cls):
        global _cache
        if _cache is None:
            _cache = super().__new__(cls)
        return _cache

    def prepare(self):
        load_sources()
        self.db.prepare()
        self.mail.prepare()
        self.users.prepare()
        self.scheduler.start()

    def cleanup(self):
        self.db.close()
        self.mail.close()
        self.scheduler.close()
        global _cache
        _cache = None

    @cached_property
    def config(self):
        from .config import Config
        return Config()

    @cached_property
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
    def scheduler(self):
        from .services.scheduler import JobScheduler
        return JobScheduler(self)

    @cached_property
    def fetch(self):
        from .services.fetch import FetchService
        return FetchService(self)

    @cached_property
    def metadata(self):
        from .services.meta import MetadataService
        return MetadataService(self)

    @cached_property
    def mail(self):
        from .services.mail import MailService
        return MailService(self)
