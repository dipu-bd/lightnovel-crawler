from ....context import ctx
from ....enums import JobType, OutputFormat
from ._base import AbortedException, BatchHandler, HandlerException


class ArtifactBatchHandler(BatchHandler):
    @staticmethod
    def can_activate(job) -> bool:
        return job.type == JobType.ARTIFACT_BATCH

    def run(self) -> None:
        formats = self.job.extra.get("formats")
        if not formats:
            return

        novel_id = self.job.extra.get("novel_id")
        if not novel_id:
            raise HandlerException("No novel id")

        format_job_map = {}
        if self.job.is_running:
            format_job_map = {
                OutputFormat(job.extra.get("format")): job.id for job in self.children
            }
        else:
            self._set_running()

        added_format = set(format_job_map.keys())
        formats = set(map(OutputFormat, formats))
        need_epub = formats & ctx.binder.depends_on_epub
        if need_epub:
            formats.add(OutputFormat.epub)

        if not formats:
            return

        for format in sorted(formats - need_epub - added_format):
            if self.signal.is_set():
                raise AbortedException()
            job = self._create_job(novel_id, format, None)
            format_job_map[format] = job.id

        if need_epub:
            epub_job_id = format_job_map.get(OutputFormat.epub)
            if not epub_job_id:
                raise HandlerException("No epub request found")
            for format in sorted(need_epub - added_format):
                if self.signal.is_set():
                    raise AbortedException()
                self._create_job(novel_id, format, epub_job_id)

    def _create_job(self, novel_id, format, epub_job_id):
        return ctx.jobs.make_artifact(
            self.user,
            novel_id,
            format,
            parent_id=self.job.id,
            depends_on=epub_job_id,
            language=self.job.extra.get("language"),
            volume=self.job.extra.get("volume"),
            novel_title=self.job.extra.get("novel_title"),
        )
