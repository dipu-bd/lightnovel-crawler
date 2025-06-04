from typing import Optional

from box import Box

from .novel import Novel
from .session import Session


class MetaInfo(Box):
    def __init__(
        self,
        session: Optional[Session] = None,
        novel: Optional[Novel] = None,
        **kwargs,
    ) -> None:
        self.session = session
        self.novel = novel
        self.update(kwargs)
