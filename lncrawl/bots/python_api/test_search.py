import sys
import os
import json
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from lncrawl.bots.python_api import PythonApiBot


def print_response(title, response):
    """Pretty print API responses"""
    print(f"\n=== {title} ===")
    print(json.dumps(response, indent=2))


def main():
    # Initialize the bot
    bot = PythonApiBot()
    print_response("Starting bot", bot.start())

    # Create a new app session
    print_response("Init app", bot.init_app())

    # Search for a novel
    search_query = "Cadı Avcısı Sistemi"
    print_response(f"Searching for: {search_query}", bot.start_search(search_query))

    # Wait for search to complete
    print("\n=== Waiting for search to complete ===")
    last_status = None
    while True:
        status = bot.get_search_status()
        if status != last_status:
            last_status = status
            print_response("Search status", status)

        if status["search_completed"]:
            break
        if not status["search_in_progress"]:
            break

        time.sleep(1)

    # Get search results
    search_results = bot.get_search_results()
    print_response("Search results", search_results)

    # Select the first novel from search results
    if search_results["status"] == "success":
        if "direct_novel" in search_results and search_results["direct_novel"]:
            # Direct novel URL was detected, no need to select
            print("\n=== Direct novel URL detected ===")
        else:
            # Select the first novel from the first result
            print("\n=== Selecting first novel ===")
            selected = bot.select_novel(novel_index=0, source_index=0)
            print_response("Selected novel", selected)

    # Get novel info
    print_response("Novel info", bot.get_novel_info())

    # Set output path
    print_response("Setting output path", bot.set_output_path("test_search_novel"))

    # Select first 2 chapters
    print_response("Selecting first 2 chapters", bot.select_chapters("first", 2))

    # Download as JSON format
    print_response(
        "Starting download", bot.start_download(["json"], pack_by_volume=False)
    )

    # Wait for download to complete
    last_status = None
    while True:
        status = bot.get_download_status()
        if status != last_status:
            last_status = status
            print_response("Download status", status)

        if status["download_completed"]:
            break
        if not status["download_in_progress"]:
            break

        time.sleep(1)

    print_response("Download completed", bot.get_download_results())

    # Clean up
    print_response("Destroying app", bot.destroy_app())


if __name__ == "__main__":
    main()
