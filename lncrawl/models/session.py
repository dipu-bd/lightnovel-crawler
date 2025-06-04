from typing import Dict, List, Optional, Tuple

from box import Box

from .formats import OutputFormat


class Session(Box):
    def __init__(
        self,
        user_input: str = "",
        output_path: str = "",
        completed: bool = False,
        book_cover: Optional[str] = None,
        pack_by_volume: bool = False,
        chapters_to_download: List[int] = [],
        good_file_name: str = "",
        no_append_after_filename: bool = False,
        login_data: Optional[Tuple[str, str]] = None,
        output_formats: Dict[OutputFormat, bool] = dict(),
        headers: Dict[str, str] = dict(),
        cookies: Dict[str, str] = dict(),
        proxies: Dict[str, str] = dict(),
        generated_archives: Dict[OutputFormat, str] = dict(),
        generated_books: Dict[OutputFormat, List[str]] = dict(),
        search_progress: float = 0,
        fetch_novel_progress: float = 0,
        fetch_content_progress: float = 0,
        fetch_images_progress: float = 0,
        binding_progress: float = 0,
        ** kwargs,
    ) -> None:
        self.user_input = user_input
        self.output_path = output_path
        self.completed = completed
        self.book_cover = book_cover
        self.pack_by_volume = pack_by_volume
        self.chapters_to_download = chapters_to_download
        self.good_file_name = good_file_name
        self.no_append_after_filename = no_append_after_filename
        self.login_data = login_data
        self.output_formats = output_formats
        self.headers = headers
        self.cookies = cookies
        self.proxies = proxies
        self.generated_books = generated_books
        self.generated_archives = generated_archives
        self.search_progress = search_progress
        self.fetch_novel_progress = fetch_novel_progress
        self.fetch_content_progress = fetch_content_progress
        self.fetch_images_progress = fetch_images_progress
        self.binding_progress = binding_progress
        self.update(kwargs)
