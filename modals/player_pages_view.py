import math

import discord

import config
from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class PlayerPagesView(discord.ui.View):

    PAGE_SIZE = config.MAX_PAGES_PER_PAGE

    def __init__(
            self,
            bot,
            user: discord.User | discord.Member,
            collection_id: int | None = None,
            collection_name: str | None = None
    ):
        super().__init__(timeout=300)

        self.bot = bot
        self.user = user

        self.collection_id = collection_id
        self.collection_name = collection_name

        self.page = 0

        self.entries = []
        self.total_pages = 0
        self.max_pages = 1

        self.update_buttons()

    async def load_page(self):

        library = await self.bot.player_service.get_player_library(
            self.user,
            self.PAGE_SIZE,
            self.page * self.PAGE_SIZE,
            collection_id=self.collection_id
        )

        self.entries = library.entries
        self.total_pages = library.total_pages

        self.max_pages = max(
            1,
            math.ceil(
                self.total_pages / self.PAGE_SIZE
            )
        )

        self.update_buttons()

    def build_embed(self):

        lines = ["🔴 Undiscovered • 🟠 Unclaimed • 🟢 Claimed • 👑 First Claim\n"]

        for page in self.entries:

            if not page.discovered:

                lines.append(
                    f"🔴 `{page.page_id:03}` "
                    f"Not Discovered"
                )

                continue

            _status = "🟢" if page.claimed else "🟠"

            status = "👑" if page.original_owner else _status

            rarity = "⭐" * int(page.rarity)

            lines.append(
                f"{status} "
                f"`{page.page_id:03}` "
                f"{rarity} "
                f"{page.name} "
                f"×{page.amount}"
            )

        embed = EmbedFactory.create(
            title=(
                f"📖 {self.user.display_name}'s "
                f"{self.collection_name} Pages"
                if self.collection_name
                else f"📖 {self.user.display_name}'s Pages"
            ),
            description="\n".join(lines),
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.user.display_avatar.url
        )

        embed.set_footer(
            text=(
                f"Page {self.page + 1}/{self.max_pages}"
            )
        )

        return embed

    def update_buttons(self):

        self.previous.disabled = self.page == 0

        self.next.disabled = (
            self.page >= self.max_pages - 1
        )

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

        await self.load_page()

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

        await self.load_page()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )