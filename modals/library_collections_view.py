import math
import discord
import config
from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class LibraryCollectionsView(discord.ui.View):

    PAGE_SIZE = config.COLLECTION_PAGE_SIZE

    def __init__(
            self,
            bot,
            collections
    ):
        super().__init__(timeout=300)

        self.bot = bot
        self.collections = collections

        self.page = 0

        self.max_pages = max(
            1,
            math.ceil(len(collections) / self.PAGE_SIZE)
        )

        self.update_buttons()

    def update_buttons(self):
        self.previous.disabled = self.page == 0
        self.next.disabled = self.page >= self.max_pages - 1

    def build_embed(self):

        start = self.page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE

        lines = []

        claimed_total = 0
        page_total = 0

        for collection in self.collections[start:end]:

            percentage = (
                collection.claimed_pages
                / collection.total_pages
                * 100
                if collection.total_pages
                else 0
            )

            claimed_total += collection.claimed_pages
            page_total += collection.total_pages

            progress = round(percentage / 10)

            progress_bar = (
                "🟩" * progress
                + "⬜" * (10 - progress)
            )

            lines.append(
                f"**{collection.collection_name}**\n"
                f"{progress_bar}\n"
                f"👑 {collection.claimed_pages}/{collection.total_pages}"
                f" ({percentage:.1f}%)"
            )

        overall = (
            claimed_total / page_total * 100
            if page_total else 0
        )

        embed = EmbedFactory.create(
            title="📚 Global Collection Progress",
            description="\n\n".join(lines),
            colour=Colours.INFO
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.set_footer(
            text=(
                f"Page {self.page + 1}/{self.max_pages}"
                f" • Overall: {overall:.1f}%"
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