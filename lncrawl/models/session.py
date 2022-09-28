from typing import Dict, List, Optional

from box import Box

from .formats import OutputFormat


class Session(Box):
    def __init__(
        self,
        user_input: str,
        login_data: str,
        output_path: str,
        completed: bool = False,
        pack_by_volume: bool = False,
        download_chapters: List[int] = [],
        good_file_name: Optional[str] = None,
        no_append_after_filename: bool = False,
        output_formats: Dict[OutputFormat, bool] = dict(),
    ) -> None:
        self.user_input = user_input
        self.login_data = login_data
        self.output_path = output_path
        self.completed = completed
        self.pack_by_volume = pack_by_volume
        self.download_chapters = download_chapters
        self.good_file_name = good_file_name
        self.no_append_after_filename = no_append_after_filename
        self.output_formats = output_formats
