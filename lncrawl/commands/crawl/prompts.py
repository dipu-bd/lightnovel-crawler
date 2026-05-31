from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Sequence, Set, Tuple, Union

import questionary
from rich import print

from ...context import ctx
from ...dao import Novel, Volume
from ...enums import OutputFormat
from ...utils.url_tools import validate_url

if TYPE_CHECKING:
    from ...dao import Chapter

logger = logging.getLogger(__name__)

max_retry_attempts = 1
ChapterGroup = Union["Chapter", Tuple[int, int, List["ChapterGroup"]]]


def prompt_login_details() -> Tuple[Optional[str], Optional[str]]:
    wants_login = questionary.confirm(
        "Do you want to login?",
        qmark="🔒",
        default=True,
    ).ask()
    if not wants_login:
        return (None, None)
    username = questionary.text(
        "Username/Email:",
        qmark="🔒",
    ).ask(kbi_msg="")
    password = questionary.text(
        "Password/Token:",
        qmark="🔒",
    ).ask(kbi_msg="")
    return (username, password)


def prompt_url() -> str:
    print("[i]The URL must start with [cyan]http[/cyan] or [cyan]https[/cyan].[/i]")
    return questionary.text(
        "Novel page URL:",
        qmark="🌐",
        validate=validate_url,
    ).ask()


def prompt_range_selection(novel: Novel, attempt=0) -> List[str]:
    choices = [
        questionary.Choice("All chapters", value="all"),
        questionary.Choice("Not yet downloaded chapters", value="new"),
    ]
    if novel.volume_count > 1:
        choices += [
            questionary.Choice(f"Select volumes ({novel.volume_count} items)", value="volumes"),
        ]
    if novel.chapter_count > 1:
        choices += [
            questionary.Choice(f"Select chapters ({novel.chapter_count} items)", value="chapters"),
        ]
    choices += [
        questionary.Choice("Downloaded chapters only", value="old"),
        questionary.Choice("Exit", value="exit", shortcut_key="0"),
    ]

    choice = questionary.select(
        "Select chapters to download",
        choices=choices,
        default="new",
        use_shortcuts=True,
    ).ask(kbi_msg="")

    if choice == "all":
        return ctx.chapters.list_ids(novel_id=novel.id)

    if choice == "new" or choice == "old":
        return ctx.chapters.list_ids(
            novel_id=novel.id,
            is_crawled=(choice == "old"),
        )

    if choice == "volumes":
        volumes = ctx.volumes.list(novel.id)
        voluem_ids = prompt_select_volumes(volumes)
        if voluem_ids:
            return [
                chapter_id
                for volume_id in voluem_ids
                for chapter_id in ctx.chapters.list_ids(volume_id=volume_id)
            ]

    if choice == "chapters":
        chapters = ctx.chapters.list(novel_id=novel.id)
        chapter_ids = prompt_select_chapters(chapters)
        if chapter_ids:
            return chapter_ids

    if choice == "exit":
        raise KeyboardInterrupt()

    if attempt >= max_retry_attempts:
        raise KeyboardInterrupt()

    print("[red]Please make your choice![/red]")
    print(f"[i]You have {max_retry_attempts - attempt} more chance.[/i]\n")
    return prompt_range_selection(novel, attempt + 1)


def prompt_select_volumes(volumes: List[Volume], attempt=0) -> List[str]:
    volume_ids = questionary.checkbox(
        "Choose volumes to download:",
        choices=[
            questionary.Choice(
                value=volume.id,
                title=volume.title,
            )
            for volume in volumes
        ],
        validate=lambda c: True if c else "Select at least one item",
    ).ask(kbi_msg="")

    if volume_ids:
        return volume_ids

    if attempt >= max_retry_attempts:
        print()
        return []

    print("[red]Please select at least one volume[/red]\n")
    return prompt_select_volumes(volumes, attempt + 1)


def prompt_select_chapters(groups: Sequence[ChapterGroup], attempt=0) -> List[str]:
    from ...dao import Chapter

    assert isinstance(groups, list)
    # Group chapters into smaller chunks (as there can be more than 50,000)
    # Following code creates a Balanced Tree where each node will have at most k=20 children
    k = 20
    while len(groups) > k:
        new_groups: List[ChapterGroup] = []
        for i in range(0, len(groups), k):
            chunk = groups[i : i + k]
            a = chunk[0]
            b = chunk[-1]
            sa = a.serial if isinstance(a, Chapter) else a[0]
            sb = b.serial if isinstance(b, Chapter) else b[0]
            new_groups.append((sa, sb, chunk))
        groups = new_groups

    # Make selected from the Balanced Tree
    selected: Set[str] = set()
    stack: List[List[ChapterGroup]] = [groups]
    while len(stack) > 0:
        # Get the last node from the stack
        current = stack[-1]

        # Some helpful text
        if len(selected) > 0:
            print(
                f"{len(selected)} chapters are selected.",
                '[i]You can select more or choose "Done" to finish.[/i]',
            )

        # If this is a leaf node it will have list of chapters.
        # Get selection of one or more chapters from user and continue.
        if isinstance(current[0], Chapter):
            chapter_ids = questionary.checkbox(
                "Choose chapters to download:",
                choices=[
                    questionary.Choice(
                        value=chapter.id,
                        title=f"{chapter.serial}) {chapter.title}",
                        checked=(chapter.id in selected),
                    )
                    for chapter in current
                    if isinstance(chapter, Chapter)
                ],
            ).ask(kbi_msg="")
            for id in chapter_ids:
                selected.add(id)
            stack.pop()  # pop after processing this node
            continue

        # Oherwise if not a leaf node, it is a chapter group node
        # Get selection of a single group to select chapters from it
        choice = questionary.select(
            "Select chapters:",
            use_shortcuts=True,
            choices=[questionary.Choice("Done", value="done")]
            + [
                questionary.Choice(
                    value=index,
                    title=f"Chapters {node[0]}-{node[1]}",
                )
                for index, node in enumerate(current)
                if isinstance(node, tuple)
            ]
            + [questionary.Choice("Back", value="back", shortcut_key="0")],
        ).ask(kbi_msg="")

        if choice == "done":
            break  # no more selection

        if isinstance(choice, int):
            # select current node group
            item = current[choice]
            if isinstance(item, tuple):
                stack.append(item[2])
            elif isinstance(item, list):
                stack.append(item)
            continue

        # handle default choice: 'back'
        stack.pop()  # pop last node from stack to go back
        continue

    if selected:
        return list(selected)

    if attempt >= max_retry_attempts:
        print()
        return []

    print("[red]Please select at least one chapter[/red]\n")
    return prompt_select_chapters(groups, attempt + 1)


def prompt_format_selection() -> List[OutputFormat]:
    defaults = [OutputFormat.epub, OutputFormat.json]
    result = questionary.checkbox(
        "Select novel output formats:",
        choices=[
            questionary.Choice(
                value=fmt,
                title=fmt.value,
                checked=fmt in defaults,
            )
            for fmt in list(OutputFormat)
            if fmt in ctx.binder.available_formats
        ],
    ).ask(kbi_msg="")
    if not result:
        return [OutputFormat.epub]
    return result


def prompt_open_artifact_folder() -> bool:
    return questionary.confirm(
        "Open the artifact folder?",
        default=True,
    ).ask(kbi_msg="")
