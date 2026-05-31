from email.mime.text import MIMEText
import logging
from smtplib import SMTP
from typing import Optional

import lxml.etree
import lxml.html

from ..assets import emails
from ..context import ctx
from ..dao import Job, JobStatus, User
from ..exceptions import ServerErrors
from ..utils.file_tools import format_size

logger = logging.getLogger(__name__)


class MailService:
    def __init__(self) -> None:
        self.server: Optional[SMTP] = None
        self.sender = ctx.config.mail.smtp_sender or ctx.config.mail.smtp_username

    def close(self):
        if self.server:
            self.server.close()
            self.server = None

    def prepare(self):
        if self.server:
            return

        smtp_server = ctx.config.mail.smtp_server
        smtp_port = ctx.config.mail.smtp_port
        smtp_user = ctx.config.mail.smtp_username
        smtp_pass = ctx.config.mail.smtp_password
        if not all([smtp_server, smtp_port, smtp_user, smtp_pass]):
            raise ServerErrors.smtp_server_unavailable

        try:
            logger.info("Preparing mail server")
            self.server = SMTP(smtp_server, smtp_port)
            self.server.starttls()
            self.server.login(smtp_user, smtp_pass)
            logger.info(f"Connected with SMTP server: {smtp_server}")
        except Exception as e:
            self.close()
            raise ServerErrors.smtp_server_login_fail from e

    def send(self, email: str, subject: str, html_body: str):
        # Prepare mail server
        self.prepare()

        # Minify HTML
        tree = lxml.html.fromstring(html_body)
        minified = lxml.etree.tostring(tree, encoding="unicode", pretty_print=False)

        # Create mail body
        msg = MIMEText(minified, "html")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = email

        try:
            assert self.server
            self.server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        except Exception as e:
            raise ServerErrors.email_send_failure from e

    def send_invite(self, email: str, inviter_name: str, link: str):
        subject = "Lightnovel Crawler Invitation"
        body = emails.invite_template().render(inviter_name=inviter_name, link=link)
        self.send(email, subject, body)

    def send_otp(self, email: str, otp: str):
        subject = f"OTP ({otp})"
        body = emails.otp_template().render(otp=otp)
        self.send(email, subject, body)

    def send_reset_password_link(self, email: str, link: str):
        subject = "Reset Password"
        body = emails.repass_template().render(link=link)
        self.send(email, subject, body)

    def send_full_novel_job_success(self, user: User, job: Job):
        novel_id = job.extra.get("novel_id")
        if not novel_id:
            return

        novel = ctx.novels.get(novel_id)
        artifacts = ctx.artifacts.list_latest(novel.id)

        base_url = ctx.config.server.base_url
        job_url = f"{base_url}/job/{job.id}"
        novel_title = novel.title or "Unknown"
        novel_authors = novel.authors or "Unknown"
        chapter_count = novel.chapter_count or "?"
        volume_count = novel.volume_count or "?"
        novel_synopsis = novel.synopsis or ""

        token = ctx.users.generate_token(user, 30 * 24 * 60)
        artifacts = [
            {
                "format": str(item.format),
                "size": format_size(item.file_size or 0),
                "name": ctx.files.resolve(item.output_file).name,
                "url": f"{base_url}/static/{item.output_file}?token={token}",
            }
            for item in artifacts
        ]

        if len(novel_synopsis) > 300:
            novel_synopsis = f"{novel_synopsis[:300]}..."

        body = emails.job_full_novel_template().render(
            job_url=job_url,
            artifacts=artifacts,
            novel_title=novel_title,
            novel_authors=novel_authors,
            chapter_count=chapter_count,
            volume_count=volume_count,
            novel_synopsis=novel_synopsis,
        )

        self.send(user.email, novel_title, body)

    def send_job_report(self, user: User, job: Job):
        base_url = ctx.config.server.base_url
        job_url = f"{base_url}/job/{job.id}"
        error = (job.error or "").strip().split("\n")[-1]
        job_type = job.type.name.lower().replace("_", " ").title()
        job_status = job.status.name.lower().replace("_", " ").title()
        subject = f"{job_status}: {job_type}"
        body = emails.job_status_template().render(
            failure=error,
            job_url=job_url,
            job_type=job_type,
            job_status=job_status,
            job_title=job.job_title,
            is_running=job.status == JobStatus.RUNNING,
            is_success=job.status == JobStatus.SUCCESS,
            is_canceled=job.status == JobStatus.CANCELED,
            is_failed=job.status == JobStatus.FAILED,
        )
        self.send(user.email, subject, body)
