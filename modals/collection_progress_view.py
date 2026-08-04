import math

import discord

import config
from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class CollectionProgressView(discord.ui.View):

    PAGE_SIZE = config.COLLECTION_PAGE_SIZE

    def __init__(
            self,
            user: discord.abc.User,
            progress
    ):
        super().__init__(timeout=300)

        self.user = user
        self.progress = progress

        self.page = 0

        self.max_pages = max(
            1,
            math.ceil(len(progress) / self.PAGE_SIZE)
        )

        self.update_buttons()

    def update_buttons(self):
        self.previous.disabled = self.page == 0
        self.next.disabled = self.page >= self.max_pages - 1

    def build_embed(self):

        start = self.page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE

        lines = []

        for collection in self.progress[start:end]:

            progress_bar = (
                "🟩" * round(collection.completion_percentage / 10)
                + "⬜" * (10 - round(collection.completion_percentage / 10))
            )

            lines.append(
                f"**{collection.collection_name}**\n"
                f"{progress_bar}\n"
                f"📖 {collection.collected_pages}/{collection.total_pages} "
                f"({collection.completion_percentage:.1f}%)"
                f" • 👑 {collection.claimed_pages} First Claims\n"
            )

        embed = EmbedFactory.create(
            title="📚 Collection Progress",
            description="\n".join(lines),
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.user.display_avatar.url
        )

        embed.set_footer(
            text=(
                f"Page {self.page + 1}/{self.max_pages} • "
                "Collect every page to complete your own Book!"
            )
        )

        return embed

    @discord.ui.button(
        emoji="◀️",
        style=discord.ButtonStyle.secondary
    )
    async def previous(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.page -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="▶️",
        style=discord.ButtonStyle.secondary
    )
    async def next(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.page += 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )