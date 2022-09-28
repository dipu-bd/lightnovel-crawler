from box import Box

from .novel import Novel
from .session import Session


class Session(Box):
    def __init__(
        self,
        novel: Novel,
        session: Session,
    ) -> None:
        self.novel = novel
        self.session = session
