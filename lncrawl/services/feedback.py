from datetime import datetime
import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from scraper import extract_host

from ..dao import User
from ..enums import FeedbackStatus, FeedbackType, UserRole
from ..exceptions import ServerErrors
from ..server.models import Feedback, Paginated
from ..utils.github import GithubClient

# Marks issues created through the app, so the feedback page only shows these.
_APP_LABEL = "app-feedback"
# Marks an accepted (in-progress) feedback. Closed issues are "resolved".
_ACCEPTED_LABEL = "feedback:accepted"
# Feedback type <-> GitHub label mapping.
_TYPE_LABELS: Dict[FeedbackType, str] = {
    FeedbackType.GENERAL: "feedback:general",
    FeedbackType.ISSUE: "feedback:bug",
    FeedbackType.FEATURE: "feedback:feature",
}
_LABEL_TO_TYPE: Dict[str, FeedbackType] = {v: k for k, v in _TYPE_LABELS.items()}

# Hidden metadata block embedded at the end of the issue body to carry
# internal references (linked job/novel ids) without exposing extra UI noise.
_META_RE = re.compile(r"\n*<!--\s*lncrawl:meta\s+(\{.*?\})\s*-->\s*$", re.DOTALL)
# Only these keys are persisted in the metadata block (used by the UI to link
# the feedback to a job/novel/chapter). Everything else is dropped.
_META_KEYS = ("job_id", "novel_id", "chapter_id")


class FeedbackService:
    def __init__(self) -> None:
        pass

    # -- helpers ----------------------------------------------------------

    def _user_hash(self, user: User) -> str:
        return hashlib.shake_256(user.email.encode()).hexdigest(6)

    def _user_label(self, user: User) -> str:
        return f"user:{self._user_hash(user)}"

    def _issue_number(self, feedback_id: str) -> int:
        try:
            return int(feedback_id)
        except (TypeError, ValueError):
            raise ServerErrors.not_found

    def _meta_block(self, meta: Dict[str, Any]) -> str:
        data = {k: meta[k] for k in _META_KEYS if meta.get(k)}
        if not data:
            return ""
        return f"\n\n<!-- lncrawl:meta {json.dumps(data)} -->"

    def _build_body(self, message: str, meta: Dict[str, Any]) -> str:
        """The issue body is the user-confirmed message (which already carries
        any request details, error log and web app links) plus a hidden block
        of metadata used to link the feedback to a job/novel in the app."""
        return (message or "").strip() + self._meta_block(meta)

    def _source_labels(self, type: FeedbackType, url: Optional[str]) -> List[str]:
        domain = extract_host(url) if url else ""
        if not domain:
            return []
        labels = [f"source:{domain}"]
        if type == FeedbackType.ISSUE:
            labels.append("source-bug")
        return labels

    def _extract_meta(self, body: Optional[str]) -> Tuple[str, Dict[str, Any]]:
        if not body:
            return "", {}
        match = _META_RE.search(body)
        if not match:
            return body.strip(), {}
        try:
            extra = json.loads(match.group(1))
        except json.JSONDecodeError:
            extra = {}
        return body[: match.start()].strip(), extra

    def _iso_to_ms(self, value: Optional[str]) -> int:
        if not value:
            return 0
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return round(dt.timestamp() * 1000)
        except ValueError:
            return 0

    def _ensure_owner(self, user: User, issue: dict) -> None:
        if user.role == UserRole.ADMIN:
            return
        labels = {lb["name"] for lb in issue.get("labels", [])}
        if self._user_label(user) not in labels:
            raise ServerErrors.forbidden

    def _to_feedback(self, issue: dict, *, user_hash: Optional[str] = None) -> Feedback:
        labels = {lb["name"] for lb in issue.get("labels", [])}

        type = FeedbackType.GENERAL
        for label in labels:
            if label in _LABEL_TO_TYPE:
                type = _LABEL_TO_TYPE[label]
                break

        if issue.get("state") == "closed":
            status = FeedbackStatus.RESOLVED
        elif _ACCEPTED_LABEL in labels:
            status = FeedbackStatus.ACCEPTED
        else:
            status = FeedbackStatus.PENDING

        message, meta = self._extract_meta(issue.get("body"))
        extra = {k: meta[k] for k in _META_KEYS if meta.get(k)}
        is_mine = bool(user_hash and f"user:{user_hash}" in labels)

        return Feedback(
            id=str(issue["number"]),
            type=type,
            status=status,
            subject=issue.get("title") or "",
            message=message,
            created_at=self._iso_to_ms(issue.get("created_at")),
            updated_at=self._iso_to_ms(issue.get("updated_at")),
            html_url=issue.get("html_url") or "",
            is_mine=is_mine,
            extra=extra,
        )

    # -- operations -------------------------------------------------------

    def create(
        self,
        user: User,
        *,
        type: FeedbackType,
        subject: str,
        message: str,
        extra: Dict[str, Any],
    ) -> Feedback:
        meta = {k: extra[k] for k in _META_KEYS if extra.get(k)}
        labels = [_APP_LABEL, _TYPE_LABELS[type], self._user_label(user)]
        labels += self._source_labels(type, extra.get("url"))

        with GithubClient() as gh:
            # Create first, then attach labels: the add-labels endpoint
            # auto-creates labels that do not exist in the repo yet, while the
            # create-issue endpoint can silently drop unknown labels.
            issue = gh.create_issue(
                title=subject,
                body=self._build_body(message, meta),
                labels=[],
            )
            issue["labels"] = gh.add_labels(str(issue["number"]), labels)
        return self._to_feedback(issue, user_hash=self._user_hash(user))

    def list(
        self,
        user: User,
        offset: int = 0,
        limit: int = 20,
        *,
        search: str = "",
        status: Optional[FeedbackStatus] = None,
        type: Optional[FeedbackType] = None,
        mine: bool = False,
    ) -> Paginated[Feedback]:
        query: List[str] = [f'label:"{_APP_LABEL}"']

        if type is not None:
            query.append(f'label:"{_TYPE_LABELS[type]}"')

        if status == FeedbackStatus.RESOLVED:
            query.append("is:closed")
        elif status == FeedbackStatus.ACCEPTED:
            query.append(f'is:open label:"{_ACCEPTED_LABEL}"')
        elif status == FeedbackStatus.PENDING:
            query.append(f'is:open -label:"{_ACCEPTED_LABEL}"')

        if mine:
            query.append(f'label:"{self._user_label(user)}"')

        if search:
            query.append(search)

        page = offset // limit + 1 if limit else 1
        with GithubClient() as gh:
            result = gh.search_issues(" ".join(query), page=page, per_page=limit)

        user_hash = self._user_hash(user)
        items = [self._to_feedback(issue, user_hash=user_hash) for issue in result.get("items", [])]
        # The GitHub search API caps total_count at 1000.
        total = min(int(result.get("total_count", 0)), 1000)

        return Paginated(
            total=total,
            offset=offset,
            limit=limit,
            items=items,
        )

    def get(self, user: User, feedback_id: str) -> Feedback:
        number = self._issue_number(feedback_id)
        with GithubClient() as gh:
            try:
                issue = gh.get_issue(number)
            except httpx.HTTPStatusError as err:
                if err.response.status_code == 404:
                    raise ServerErrors.not_found
                raise
        if issue.get("pull_request"):
            raise ServerErrors.not_found
        return self._to_feedback(issue, user_hash=self._user_hash(user))

    def update(
        self,
        user: User,
        feedback_id: str,
        *,
        subject: Optional[str] = None,
        message: Optional[str] = None,
        type: Optional[FeedbackType] = None,
    ) -> Feedback:
        number = self._issue_number(feedback_id)
        with GithubClient() as gh:
            issue = gh.get_issue(number)
            if issue.get("pull_request"):
                raise ServerErrors.not_found
            self._ensure_owner(user, issue)

            body: Optional[str] = None
            if message is not None:
                _, meta = self._extract_meta(issue.get("body"))
                body = self._build_body(message, meta)

            labels: Optional[List[str]] = None
            if type is not None:
                kept = [
                    lb["name"] for lb in issue.get("labels", []) if lb["name"] not in _LABEL_TO_TYPE
                ]
                kept.append(_TYPE_LABELS[type])
                labels = kept

            updated = gh.update_issue(number, title=subject, body=body, labels=labels)
        return self._to_feedback(updated, user_hash=self._user_hash(user))

    def respond(
        self,
        user: User,
        feedback_id: str,
        *,
        status: FeedbackStatus,
    ) -> Feedback:
        if user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden

        number = self._issue_number(feedback_id)
        with GithubClient() as gh:
            issue = gh.get_issue(number)
            if issue.get("pull_request"):
                raise ServerErrors.not_found

            labels = [lb["name"] for lb in issue.get("labels", []) if lb["name"] != _ACCEPTED_LABEL]
            if status == FeedbackStatus.RESOLVED:
                state = "closed"
            else:
                state = "open"
                if status == FeedbackStatus.ACCEPTED:
                    labels.append(_ACCEPTED_LABEL)

            updated = gh.update_issue(number, state=state, labels=labels)
        return self._to_feedback(updated, user_hash=self._user_hash(user))

    def delete(self, user: User, feedback_id: str) -> bool:
        number = self._issue_number(feedback_id)
        with GithubClient() as gh:
            try:
                issue = gh.get_issue(number)
            except httpx.HTTPStatusError as err:
                if err.response.status_code == 404:
                    return True
                raise
            if issue.get("pull_request"):
                return True
            self._ensure_owner(user, issue)
            gh.delete_issue(issue["node_id"])
        return True
