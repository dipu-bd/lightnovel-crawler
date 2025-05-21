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

    # Alternative: Direct URL usage
    print("\n=== Testing direct URL ===")
    direct_url = "https://fenrirscans.com/seriler/cadi-avcisi-sistemi/"
    print_response("Setting novel URL", bot.set_novel_url(direct_url))

    print_response("Setting output path", bot.set_output_path("test_novel"))

    # Select chapters from direct URL novel
    print_response("Selecting first 2 chapters", bot.select_chapters("first", 2))

    # Download in multiple formats
    print_response(
        "Downloading multiple formats",
        bot.start_download(["json"], pack_by_volume=False),
    )

    # await for download completion
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
