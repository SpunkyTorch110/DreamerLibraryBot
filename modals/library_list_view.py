import math

import discord
from discord import ButtonStyle, Embed

import config
from embeds.embed_factory import EmbedFactory
from models.library_page_entry import LibraryPageEntry
from utils.colours import Colours


class LibraryListView(discord.ui.View):

    PAGE_SIZE = config.MAX_PAGES_PER_PAGE

    def __init__(
            self,
            bot,
            entries: list[LibraryPageEntry],
            owner_id: int
    ):
        super().__init__(timeout=300)
        self.owner_id = owner_id
        self.bot = bot
        self.entries = entries

        self.page = 0

        self.max_page = max(
            0,
            math.ceil(len(entries) / self.PAGE_SIZE) - 1
        )

        self.update_buttons()

    def build_embed(self) -> Embed:

        embed = EmbedFactory.create(
            title="📚 Global Library Page List",
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        start = self.page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE

        width = max(
            1,
            len(str(max(
                (entry.id for entry in self.entries),
                default=0
            )))
        )

        lines = ["🔴 Undiscovered • 🟠 Discovered • 🟢 Claimed\n"]

        for entry in self.entries[start:end]:

            if not entry.discovered:

                status = "🔴"

                lines.append(
                    f"{status} `{entry.id:0{width}}` • *Not Discovered*"
                )

            else:

                status = "🟢" if entry.claimed else "🟠"

                stars = "⭐" * int(entry.rarity)

                lines.append(
                    f"{status} `{entry.id:0{width}}` • **{entry.name}** {stars}"
                )

        embed.description = (
            "\n".join(lines)
            if lines
            else "*No pages found.*"
        )

        embed.set_footer(
            text=(
                f"Showing {start + 1}-{min(end, len(self.entries))} "
                f"of {len(self.entries)} • "
                f"Page {self.page + 1}/{self.max_page + 1}"
            )
        )

        return embed

    def update_buttons(self):

        self.first.disabled = self.page == 0
        self.previous.disabled = self.page == 0

        self.next.disabled = self.page >= self.max_page
        self.last.disabled = self.page >= self.max_page

    @discord.ui.button(
        emoji="⏮️",
        style=ButtonStyle.secondary
    )
    async def first(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.page = 0

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="◀️",
        style=ButtonStyle.secondary
    )
    async def previous(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.page > 0:
            self.page -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="▶️",
        style=ButtonStyle.secondary
    )
    async def next(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.page < self.max_page:
            self.page += 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="⏭️",
        style=ButtonStyle.secondary
    )
    async def last(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.page = self.max_page

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )

    async def on_timeout(self):

        for item in self.children:
            item.disabled = True

        if self.message is not None:
            await self.message.edit(view=self)

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ):

        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "You cannot control someone else's library.",
                ephemeral=True
            )

            return False

        return True