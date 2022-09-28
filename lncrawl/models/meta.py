from typing import Optional

from box import Box

from .novel import Novel
from .session import Session


class MetaInfo(Box):
    def __init__(
        self,
        novel: Optional[Novel] = None,
        session: Optional[Session] = None,
    ) -> None:
        self.novel = novel
        self.session = session
