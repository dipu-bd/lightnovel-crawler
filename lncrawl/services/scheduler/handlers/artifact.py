from ....context import ctx
from ....enums import JobType, OutputFormat
from ._base import AbortedException, BaseHandler, HandlerException

_ALL_OUTPUT_FORMATS = frozenset(OutputFormat)


class ArtifactHandler(BaseHandler):
    @staticmethod
    def can_activate(job) -> bool:
        return job.type == JobType.ARTIFACT

    def run(self) -> None:
        novel_id = self.job.extra.get("novel_id")
        if not novel_id:
            raise HandlerException("No novel id")

        format = self.job.extra.get("format")
        if not format:
            raise HandlerException("No output format")

        language = self.job.extra.get("language")
        volume = self.job.extra.get("volume")

        if format not in _ALL_OUTPUT_FORMATS:
            raise HandlerException(f"Invalid format: {format}")

        if not self.job.is_running:
            self._set_running()

        novel_title = self.job.extra.get("novel_title")
        if not novel_title:
            novel_title = ctx.novels.get(novel_id).title

        epub = None
        if format in ctx.binder.depends_on_epub:
            if not self.job.depends_on:
                raise HandlerException(f"Dependency job not found for {format}")
            epub = ctx.artifacts.get_epub(self.job.depends_on)

        if self.signal.is_set():
            raise AbortedException()

        artifact = ctx.binder.make_artifact(
            format=format,
            novel_id=novel_id,
            novel_title=novel_title,
            job_id=self.job.id,
            user_id=self.user.id,
            epub=epub,
            language=language,
            volume=volume,
            signal=self.signal,
        )
        if not artifact.is_available:
            raise HandlerException("Failed to make artifact")

        self._set_extra(artifact_id=artifact.id, novel_title=novel_title)
