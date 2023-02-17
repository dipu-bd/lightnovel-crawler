from typing import List
import discord

from lncrawl.models.search_result import CombinedSearchResult


class NovelSelectMenu(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Select a novel...",
            min_values=1,
            max_values=1,
            row=0,
        )
        self.novelList = []

    def fill_options(self, novelList: List[CombinedSearchResult]) -> None:
        self.novelList = novelList
        for i, item in enumerate(novelList):
            nc = len(item.novels)
            self.add_option(
                label=item.title,
                value=str(i),
                description=f"{nc} source{'s'[:nc^1]}",
            )

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        novel_list = [
            f"{i+1}. <{item.url}> {item.info or ''}".strip()
            for i, item in enumerate(self.novelList[int(value)].novels)
        ]

        message = ""
        novel_count = len(novel_list)
        # split into separate messages w/ length up to 2000 chars
        for i, line in enumerate(novel_list):
            message_len = len(line)
            if message_len >= 2000:
                await interaction.response.send_message(message.strip())
                message = ""
            message += line + "\n"
            if i == novel_count - 1:
                await interaction.response.send_message(message.strip())

        return


class NovelMenu(discord.ui.View):
    def add_items(self, novelList: List[CombinedSearchResult]) -> None:
        selectMenu = NovelSelectMenu()
        selectMenu.fill_options(novelList)
        self.add_item(selectMenu)
