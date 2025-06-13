import logging
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Optional

import lxml.etree
import lxml.html

from ..context import ServerContext
from ..emails import otp_template, job_template
from ..exceptions import AppErrors
from ..models.job import JobDetail, RunState

logger = logging.getLogger(__name__)


class MailService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx
        self._db = ctx.db
        self.server: Optional[SMTP] = None
        self.sender = (
            self._ctx.config.mail.smtp_sender
            or self._ctx.config.mail.smtp_username
        )

    def prepare(self):
        try:
            logger.info('Preparing mail server')
            smtp_server = self._ctx.config.mail.smtp_server
            smtp_port = self._ctx.config.mail.smtp_port
            smtp_user = self._ctx.config.mail.smtp_username
            smtp_pass = self._ctx.config.mail.smtp_password

            self.server = SMTP(smtp_server, smtp_port)
            self.server.starttls()
            self.server.login(smtp_user, smtp_pass)
            logger.info(f'Connected with SMTP server: {smtp_server}')
        except Exception:
            logger.exception('Failed to connect with SMTP server')
            self.close()

    def close(self):
        if self.server:
            self.server.close()
            self.server = None

    def send(self, email: str, subject: str, html_body: str):
        if not self.server:
            raise AppErrors.smtp_server_unavailable

        # Minify HTML
        tree = lxml.html.fromstring(html_body)
        minified = lxml.etree.tostring(tree, encoding='unicode', pretty_print=False)

        # Create mail body
        msg = MIMEText(minified, 'html')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = email

        try:
            self.server.sendmail(msg['From'], [msg['To']], msg.as_string())
        except Exception as e:
            raise AppErrors.email_send_failure from e

    def send_otp(self, email: str, otp: str):
        subject = f'OTP ({otp})'
        body = otp_template().render(otp=otp)
        self.send(email, subject, body)

    def send_job_success(self, email: str, detail: JobDetail):
        if not (
            detail
            and detail.novel
            and detail.job.run_state == RunState.SUCCESS
        ):
            raise AppErrors.server_error

        if not self.server:
            raise AppErrors.smtp_server_unavailable

        base_url = self._ctx.config.server.base_url
        job_url = f'{base_url}/job/{detail.job.id}'
        novel_title = detail.novel.title or "Unknown Title"
        novel_authors = detail.novel.authors or "Unknown Author"
        chapter_count = str(detail.novel.chapter_count or '?')
        volume_count = str(detail.novel.volume_count or '?')
        novel_synopsis = detail.novel.synopsis or "No synopsis available."
        artifacts = [
            {
                'name': item.file_name,
                'format': str(item.format),
                'url': f'{base_url}/api/artifact/{item.id}/download',
            } for item in (detail.artifacts or [])
        ]

        body = job_template().render(
            job_url=job_url,
            artifacts=artifacts,
            novel_title=novel_title,
            novel_authors=novel_authors,
            chapter_count=chapter_count,
            volume_count=volume_count,
            novel_synopsis=novel_synopsis,
        )

        self.send(email, novel_title, body)
