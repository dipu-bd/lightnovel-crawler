from typing import List

from ...context import ctx
from ...server.models import ConfigUpdateRequest
from .config import list_config_sections, update_config


class AdminService:
    def soft_restart(self):
        ctx.destroy()
        ctx.setup()
        ctx.scheduler.start()

    def config_sections(self):
        return list_config_sections()

    def update_config(self, body: List[ConfigUpdateRequest]):
        for change in body:
            update_config(change.section, change.key, change.value, dry_run=True)
        for change in body:
            update_config(change.section, change.key, change.value)
        list_config_sections.cache_clear()

    def update_sources(self) -> int:
        ctx.sources.load(False)
        ctx.sources.update()
        return ctx.sources.version
