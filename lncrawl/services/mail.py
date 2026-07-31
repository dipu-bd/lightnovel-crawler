from __future__ import annotations

from email.mime.text import MIMEText
from functools import cached_property
import logging
from smtplib import SMTP, SMTPServerDisconnected
from threading import Event, Thread

from imap_tools import AND, MailBox, MailBoxUnencrypted, MailMessage, MailMessageFlags
import lxml.etree
import lxml.html

from ..assets import emails
from ..context import ctx
from ..dao import Job, JobStatus, User
from ..exceptions import ServerError, ServerErrors
from ..utils.event_lock import EventLock
from ..utils.file_tools import format_size

logger = logging.getLogger(__name__)


def _header_safe(value: str, *, max_length: int = 998) -> str:
    """Strip CR/LF and other control characters from a header value.

    Reply threading reuses the incoming Subject / Message-ID verbatim; an RFC2047
    encoded-word can decode to bytes with embedded newlines, which makes
    `msg.as_string()` raise and (since the message is only flagged on success) wedges
    the invite handler into an endless reprocess loop. Sanitizing keeps assembly safe.
    """
    cleaned = "".join(c for c in value if c == "\t" or (c >= " " and c != "\x7f"))
    return cleaned.strip()[:max_length]


_IMAP_BACKOFF_BASE = 5
_IMAP_BACKOFF_MAX = 300
_IMAP_MAX_RETRIES = 10


class MailService:
    def __init__(self) -> None:
        self._imap_lock: Event
        self._imap_listener: Thread
        self._smtp_lock = EventLock()

    @property
    def sender(self) -> str:
        return ctx.config.mail.smtp_sender or ctx.config.mail.smtp_username

    def start(self):
        if ctx.config.mail.imap_enabled:
            logger.info("Starting Mailbox listener...")
            self._imap_lock = Event()
            self._imap_listener = Thread(
                target=self._run_imap,
                args=[self._imap_lock],
                daemon=True,
            )
            self._imap_listener.start()

    def close(self):
        self._smtp_lock.abort()
        if hasattr(self, "_imap_lock"):
            self._imap_lock.set()
        self._drop_connection()
        if hasattr(self, "_imap_listener"):
            self._imap_listener.join(timeout=5)

    @cached_property
    def server(self) -> SMTP:
        if not ctx.config.mail.smtp_enabled:
            raise ServerErrors.smtp_server_unavailable.with_extra("disabled")

        smtp_server = ctx.config.mail.smtp_server
        smtp_port = ctx.config.mail.smtp_port
        smtp_user = ctx.config.mail.smtp_username
        smtp_pass = ctx.config.mail.smtp_password
        if not all([smtp_server, smtp_port, smtp_user, smtp_pass]):
            raise ServerErrors.smtp_server_unavailable.with_extra("missing config")

        logger.info("Preparing mail server...")
        server = SMTP(smtp_server, smtp_port, timeout=30)
        try:
            if ctx.config.mail.smtp_starttls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            logger.info(f"Connected with SMTP server: {smtp_server}")
            return server
        except Exception as e:
            server.close()
            raise ServerErrors.smtp_server_login_fail from e

    def _drop_connection(self) -> None:
        server = self.__dict__.pop("server", None)
        if server is not None:
            try:
                server.close()
            except Exception:
                pass

    def _ensure_connection(self) -> SMTP:
        # SMTP servers drop idle connections; probe the cached one and
        # reconnect if it went stale
        server = self.server
        try:
            status, _ = server.noop()
        except Exception:
            status = -1
        if status != 250:
            logger.info("SMTP connection lost, reconnecting...")
            self._drop_connection()
            server = self.server
        return server

    def send(
        self,
        email: str,
        subject: str,
        html_body: str,
        *,
        in_reply_to: str | None = None,
        references: str | None = None,
    ):
        if not ctx.config.mail.smtp_enabled:
            logger.debug(f"SMTP disabled, skipping email to {email!r}")
            return

        # Minify HTML
        tree = lxml.html.fromstring(html_body)
        minified = lxml.etree.tostring(tree, encoding="unicode", pretty_print=False)

        # Create mail body
        msg = MIMEText(minified, "html")
        msg["Subject"] = _header_safe(subject, max_length=200)
        msg["From"] = self.sender
        msg["To"] = email

        in_reply_to = _header_safe(in_reply_to) if in_reply_to else None
        references = _header_safe(references) if references else None
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            chain = f"{references} {in_reply_to}".strip() if references else in_reply_to
            msg["References"] = chain

        try:
            with self._smtp_lock:
                server = self._ensure_connection()
                try:
                    server.sendmail(msg["From"], [msg["To"]], msg.as_string())
                except SMTPServerDisconnected:
                    self._drop_connection()
                    self.server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        except ServerError:
            raise
        except Exception as e:
            raise ServerErrors.email_send_failure from e

    def send_invite(
        self,
        email: str,
        inviter_name: str,
        link: str,
        *,
        reply_subject: str | None = None,
        in_reply_to: str | None = None,
        references: str | None = None,
    ):
        if reply_subject:
            subject = reply_subject.strip()
            if not subject.lower().startswith("re:"):
                subject = f"Re: {subject}"
        else:
            subject = "Lightnovel Crawler Invitation"
        body = emails.invite_template().render(inviter_name=inviter_name, link=link)
        self.send(
            email,
            subject,
            body,
            in_reply_to=in_reply_to,
            references=references,
        )

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
        error = (job.error or "").strip()
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

    # ------------------------------------------------------------------
    # IMAP inbox listener
    # ------------------------------------------------------------------

    def _run_imap(self, signal: Event):
        """Outer reconnect loop — exponential backoff, gives up after a few failures."""
        imap_server = ctx.config.mail.imap_server
        imap_port = ctx.config.mail.imap_port
        imap_user = ctx.config.mail.imap_username
        imap_pass = ctx.config.mail.imap_password
        imap_folder = ctx.config.mail.imap_folder
        if not all([imap_server, imap_port, imap_user, imap_pass]):
            raise ServerErrors.imap_server_login_fail.with_extra("missing config")

        delay, retries = _IMAP_BACKOFF_BASE, 0
        max_retry, max_delay = _IMAP_MAX_RETRIES, _IMAP_BACKOFF_MAX
        while not signal.is_set():
            try:
                server = MailBoxUnencrypted(imap_server, imap_port)
                if ctx.config.mail.imap_starttls:
                    server.client.starttls()
                with server.login(imap_user, imap_pass, imap_folder) as mb:
                    logger.info("Mailbox connected. Listenting for incoming emails...")
                    delay, retries = _IMAP_BACKOFF_BASE, 0
                    self._idle_loop(mb, signal)
            except Exception:
                retries += 1
                if retries > max_retry:
                    logger.critical(f"IMAP: {retries} consecutive failures, giving up")
                    return
                logger.exception(f"IMAP: attempt {retries}/{max_retry}, retrying in {delay}s")
                signal.wait(delay)
                delay = min(delay * 2, max_delay)

    def _idle_loop(self, mb: MailBox | MailBoxUnencrypted, signal: Event):
        """Inner per-connection loop — polls IDLE until signal or connection drops."""
        while not signal.is_set():
            responses = mb.idle.wait(timeout=3)
            if not responses:
                continue
            for msg in mb.fetch(AND(seen=False), mark_seen=False):
                self._handle_incoming(mb, msg)

    def _handle_incoming(self, mb: MailBox | MailBoxUnencrypted, msg: MailMessage):
        sender = msg.from_
        if not sender or not msg.uid:
            logger.warning(f"Something went wrong! Received null sender or uid ({msg!r})")
            return
        if ctx.users.get_user_exists(sender):
            logger.debug(f"Email from known user {sender}, skipping invite")
            return
        try:
            admin = ctx.users.get_admin()
            message_id = (msg.obj.get("Message-ID") or "").strip() or None
            references = (msg.obj.get("References") or "").strip() or None
            ctx.users.send_invite_email(
                admin,
                sender,
                reply_subject=msg.subject or None,
                in_reply_to=message_id,
                references=references,
            )
            mb.flag([msg.uid], [MailMessageFlags.SEEN, MailMessageFlags.ANSWERED], True)
            logger.info(f"Sent invite to {sender}")
        except Exception as e:
            logger.error(
                f"Failed to send invite to {sender}. {e!r}",
                exc_info=ctx.logger.is_debug,
            )
