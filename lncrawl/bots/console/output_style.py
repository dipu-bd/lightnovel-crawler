import os
import shutil

from questionary import prompt

from ...binders import available_formats
from ...core.arguments import get_args


def get_output_path(self):
    """Returns a valid output path where the files are stored"""
    args = get_args()
    output_path = args.output_path

    if args.suppress:
        if not output_path:
            output_path = self.app.output_path

        if not output_path:
            output_path = os.path.join("Lightnovels", "Unknown Novel")

    if not output_path:
        answer = prompt(
            [
                {
                    "type": "input",
                    "name": "output",
                    "message": "Enter output directory:",
                    "default": os.path.abspath(self.app.output_path),
                },
            ]
        )
        output_path = answer["output"]

    output_path = os.path.abspath(output_path)
    if os.path.exists(output_path):
        if self.force_replace_old():
            shutil.rmtree(output_path, ignore_errors=True)

    os.makedirs(output_path, exist_ok=True)

    return output_path


def force_replace_old(self):
    args = get_args()

    if args.force:
        return True
    elif args.ignore:
        return False

    if args.suppress:
        return False

    # answer = prompt([
    #     {
    #         'type': 'confirm',
    #         'name': 'force',
    #         'message': 'Detected existing folder. Replace it?',
    #         'default': False,
    #     },
    # ])
    # return answer['force']

    answer = prompt(
        [
            {
                "type": "list",
                "name": "replace",
                "message": "What to do with existing folder?",
                "choices": [
                    "Download remaining chapters only",
                    "Remove old folder and start fresh",
                ],
            },
        ]
    )
    return answer["replace"].startswith("Remove")


def get_output_formats(self):
    """Returns a dictionary of output formats."""
    args = get_args()

    defaults = ["json", "epub", "web"]
    formats = args.output_formats
    if not (formats or args.suppress):
        answer = prompt(
            [
                {
                    "type": "checkbox",
                    "name": "formats",
                    "message": "Which output formats to create?",
                    "choices": [
                        {
                            "name": x,
                            "checked": x in defaults,
                        }
                        for x in available_formats
                    ],
                },
            ]
        )
        formats = answer["formats"]

    if not formats or len(formats) == 0:
        formats = defaults  # default to epub if none selected

    return {x: (x in formats) for x in available_formats}


def should_pack_by_volume(self):
    """Returns whether to generate single or multiple files by volumes"""
    args = get_args()

    if args.single:
        return False
    elif args.multi:
        return True

    if args.suppress:
        return False

    # answer = prompt([
    #     {
    #         'type': 'confirm',
    #         'name': 'volume',
    #         'message': 'Split file by volumes?',
    #         'default': False,
    #     },
    # ])
    # return answer['volume']

    answer = prompt(
        [
            {
                "type": "list",
                "name": "split",
                "message": "How many files to generate?",
                "choices": [
                    "Pack everything into a single file",
                    "Split by volume into multiple files",
                ],
            },
        ]
    )
    return answer["split"].startswith("Split")
