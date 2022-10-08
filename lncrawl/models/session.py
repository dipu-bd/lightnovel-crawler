from typing import Dict, List, Optional, Tuple

from box import Box

from .formats import OutputFormat


class Session(Box):
    def __init__(
        self,
        user_input: str = "",
        output_path: str = "",
        completed: bool = False,
        pack_by_volume: bool = False,
        download_chapters: List[int] = [],
        good_file_name: Optional[str] = None,
        no_append_after_filename: bool = False,
        login_data: Optional[Tuple[str, str]] = None,
        output_formats: Dict[OutputFormat, bool] = dict(),
        headers: Dict[str, str] = dict(),
        cookies: Dict[str, str] = dict(),
        proxies: Dict[str, str] = dict(),
        **kwargs,
    ) -> None:
        self.user_input = user_input
        self.output_path = output_path
        self.completed = completed
        self.pack_by_volume = pack_by_volume
        self.download_chapters = download_chapters
        self.good_file_name = good_file_name
        self.no_append_after_filename = no_append_after_filename
        self.login_data = login_data
        self.output_formats = output_formats
        self.headers = headers
        self.cookies = cookies
        self.proxies = proxies
        self.update(kwargs)
