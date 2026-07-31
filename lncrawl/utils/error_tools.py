"""Splitting an exception into the part a reader needs and the part a debugger needs.

Both halves are kept in full. A job used to store its stack and its message in one
string, which left every reader — the failure email, the web UI — guessing which line
of it to show, and each of them guessed the last one. Separating them is a change of
shape, not of content: nothing here summarises, truncates or redacts.
"""

import traceback
from typing import Optional


def full_traceback(error: BaseException) -> str:
    """The complete stack behind *error*, exactly as Python formats it."""
    lines = traceback.format_exception(
        type(error),
        value=error,
        tb=error.__traceback__,
        chain=True,
    )
    return "".join(lines).strip()


def unexpected_message(error: BaseException, kind: Optional[str] = None) -> str:
    """A plain-language line for a failure nothing anticipated.

    Says outright that this is not the site refusing us, because the two want different
    responses from whoever reads it and look identical from a failed job.
    """
    what = f"{kind} job" if kind else "job"
    detail = str(error).strip()
    head = (
        f"An unexpected error stopped this {what}."
        " This is a fault in the app or in this source rather than the site refusing us."
    )
    name = type(error).__name__
    return f"{head}\n{name}: {detail}" if detail else f"{head}\n{name}"
