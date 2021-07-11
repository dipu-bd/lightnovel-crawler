# -*- coding: utf-8 -*-
from questionary import prompt

from ...assets.icons import Icons
from ...core.arguments import get_args


def display_open_folder(folder_path: str):
    args = get_args()
    if args.suppress:
        return

    answer = prompt([
        {
            'type': 'confirm',
            'name': 'exit',
            'message': 'Open the output folder?',
            'default': True,
        },
    ])

    if not answer['exit']:
        return

    if Icons.isWindows:
        import subprocess
        subprocess.Popen('explorer /select,"' + folder_path + '"')
    else:
        import pathlib
        import webbrowser
        url = pathlib.Path(folder_path).as_uri()
        webbrowser.open_new(url)
