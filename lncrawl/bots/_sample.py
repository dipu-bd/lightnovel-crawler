import logging

from ..core.app import App

logger = logging.getLogger(__name__)

# TODO: It is recommended to implemented all methods. But you can skip those
#       Which return values by default.


class SampleBot:
    def start(self):
        # TODO: must be implemented
        # Start processing using this bot. It should use self methods to take
        # inputs and self.app methods to process them.
        #
        self.app = App()
        self.app.initialize()
        #
        # Checkout console.py for a sample implementation

    def get_novel_url(self):
        # Returns a novel page url or a query
        pass

    def get_crawlers_to_search(self):
        # Returns user choice to search the choosen sites for a novel
        pass

    def choose_a_novel(self):
        # The search_results is an array of (novel_title, novel_url).
        # This method should return a single novel_url only
        #
        # By default, returns the first search_results. Implemented it to
        # handle multiple search_results
        pass

    def get_login_info(self):
        # By default, returns None to skip login
        pass

    def get_output_path(self):
        # You should return a valid absolute path. The parameter suggested_path
        # is valid but not gurranteed to exists.
        #
        # NOTE: If you do not want to use any pre-downloaded files, remove all
        #       contents inside of your selected output directory.
        #
        # By default, returns a valid existing path from suggested_path
        pass

    def get_output_formats(self):
        # The keys should be from from `self.output_formats`. Each value
        # corresponding a key defines whether create output in that format.
        #
        # By default, it returns all True to all of the output formats.
        pass

    def should_pack_by_volume(self):
        # By default, returns False to generate a single file
        pass

    def get_range_selection(self):
        # Should return a key from `self.selections` array
        pass

    def get_range_using_urls(self):
        # Should return a list of chapters to download
        pass

    def get_range_using_index(self):
        # Should return a list of chapters to download
        pass

    def get_range_from_volumes(self):
        # Should return a list of chapters to download
        pass

    def get_range_from_chapters(self):
        # Should return a list of chapters to download
        pass
