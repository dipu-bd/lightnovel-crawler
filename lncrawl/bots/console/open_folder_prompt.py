import os

from questionary import prompt

from ...utils.platforms import Platform
from ...core.arguments import get_args


def display_open_folder(folder_path: str):
    args = get_args()

    if args.suppress:
        return
    if Platform.java or Platform.docker:
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

    if Platform.windows:
        os.system(f'explorer.exe "{folder_path}"')
    elif Platform.wsl:
        os.system(f'cd "{folder_path}" && explorer.exe .')
    elif Platform.linux:
        os.system(f'xdg-open "{folder_path}"')
    elif Platform.mac:
        os.system(f'open "{folder_path}"')
    else:
        print(f"Output Folder: {folder_path}")
