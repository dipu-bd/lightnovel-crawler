import logging
import os
from typing import List, Optional

from ..context import ctx

logger = logging.getLogger(__name__)


def create_new(
    extra_args: Optional[List[str]] = None,
    timeout: Optional[float] = None,
    user_data_dir: Optional[str] = None,
    headless: bool = False,
    **kwargs,
):
    """Create a new nodriver browser instance."""
    if not user_data_dir:
        user_data_dir = str(ctx.config.app.app_dir / "webdriver")
        os.makedirs(user_data_dir, exist_ok=True)

    from .local import create_local

    return create_local(
        extra_args=extra_args,
        timeout=timeout,
        user_data_dir=user_data_dir,
        headless=headless,
    )
