import discord

from embeds.embed_factory import EmbedFactory
from embeds.page_layout import create_page_embed
from utils.colours import Colours


class PlayerGalleryView(discord.ui.View):

    def __init__(
            self,
            bot,
            player: discord.User | discord.Member,
            total: int,
            entry
    ):
        super().__init__(timeout=300)

        self.bot = bot
        self.player = player

        self.total = total
        self.current_index = 0

        self.entry = entry

        self.message: discord.Message | None = None

        self.update_buttons()

    async def load_current_entry(self):

        entries, total = await self.bot.player_service.get_player_gallery_entries(
            self.player,
            limit=1,
            offset=self.current_index
        )

        if not entries:
            return None

        self.total = total
        self.entry = entries[0]

        return self.entry

    async def build_embed(self):

        entry = await self.load_current_entry()

        if entry is None:
            return EmbedFactory.create(
                title="📚 Your Gallery",
                description="Unable to find this page in your collection.",
                colour=Colours.ERROR
            )

        page_view = await self.bot.player_service.get_player_gallery_page(
            self.player,
            entry.page_id
        )

        if page_view is None:
            return EmbedFactory.create(
                title="📚 Your Gallery",
                description="Unable to load this page.",
                colour=Colours.ERROR
            )

        page = page_view.page

        #
        # Get the current original owner.
        #

        original_owner = None

        if page.owner_id is not None:
            original_owner = await self.bot.player_service.get_discord_user(
                page.owner_id
            )

        #
        # Use the standard page layout.
        #

        embed = create_page_embed(
            page=page_view.page,
            collect=page_view.collection,
            page_image=page_view.image,
            total_pages=await self.bot.page_service.get_total_pages(),
            original_owner=original_owner,
            hide_stats=False,
            owned_amount=page_view.amount
        )

        #
        # Gallery position.
        #

        embed.set_footer(
            text=(
                f"Your Gallery • "
                f"{self.current_index + 1}/{self.total} • "
                f"Collection: {page_view.collection.name} • "
                f"{page.page_type.name.title()} • "
                f"Page Number {page.id}/"
                f"{await self.bot.page_service.get_total_pages()}"
            )
        )

        self.update_buttons()

        return embed

    def update_buttons(self):

        #
        # One page backwards
        #

        self.previous.disabled = (
            self.current_index <= 0
        )

        #
        # Five pages backwards
        #

        self.previous_five.disabled = (
            self.current_index <= 0
        )

        #
        # One page forwards
        #

        self.next.disabled = (
            self.current_index >= self.total - 1
        )

        #
        # Five pages forwards
        #

        self.next_five.disabled = (
            self.current_index >= self.total - 1
        )

    @discord.ui.button(
        emoji="⏪",
        style=discord.ButtonStyle.secondary
    )
    async def previous_five(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.current_index = max(
            0,
            self.current_index - 5
        )

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
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

        if self.current_index <= 0:
            return

        self.current_index -= 1

        await interaction.response.edit_message(
            embed=await self.build_embed(),
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

        if self.current_index >= self.total - 1:
            return

        self.current_index += 1

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="⏩",
        style=discord.ButtonStyle.secondary
    )
    async def next_five(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.current_index = min(
            self.total - 1,
            self.current_index + 5
        )

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
        )

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.player.id:

            await interaction.response.send_message(
                "Only the player who opened this gallery can use these buttons.",
                ephemeral=True
            )

            return False

        return True

    async def on_timeout(self):

        for child in self.children:
            child.disabled = True

        try:
            if self.message:
                await self.message.edit(
                    view=self
                )

        except discord.NotFound:
            pass