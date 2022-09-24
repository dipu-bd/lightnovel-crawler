import pathlib
import subprocess

from questionary import prompt

from ...assets.platforms import Platform
from ...core.arguments import get_args


def display_open_folder(folder_path: str):
    args = get_args()

    if Platform.wsl or Platform.java:
        return

    if args.suppress:
        return

    answer = prompt(
        [
            {
                "type": "confirm",
                "name": "exit",
                "message": "Open the output folder?",
                "default": True,
            },
        ]
    )

    if not answer["exit"]:
        return

    path = pathlib.Path(folder_path).as_uri()
    if Platform.windows:
        subprocess.check_call(["explorer", "/select", path])
    elif Platform.linux:
        subprocess.check_call(["xdg-open", "--", path])
    elif Platform.mac:
        subprocess.check_call(["open", "--", path])
    else:
        raise Exception("Platform is not supported")
