import discord
from discord import ButtonStyle, Embed

import config
from embeds.embed_factory import EmbedFactory
from embeds.page_layout import create_page_embed
from models.gallery_page import GalleryPage
from utils.colours import Colours


class GalleryView(discord.ui.View):

    def __init__(
            self,
            bot,
            gallery: list[GalleryPage],
            owner_id: int
    ):
        super().__init__(timeout=300)

        self.bot = bot

        self.jump_size = config.GALLERY_JUMP_SIZE

        self.gallery = gallery

        self.owner_id = owner_id

        self.index = 0

        self.message: discord.Message | None = None

        self.update_buttons()

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.owner_id:

            await interaction.response.send_message(
                "You cannot control another player's gallery.",
                ephemeral=True
            )

            return False

        return True

    async def build_embed(self) -> Embed:

        current = self.gallery[self.index]

        if not current.page.discovered:

            embed = EmbedFactory.create(
                title="Unknown Page",
                description="This page has not been discovered yet.",
                colour=Colours.INFO
            )

            embed.set_footer(
                text=f"Page {current.page.id}/{len(self.gallery)}"
            )

            return embed

        org_owner = await self.bot.player_service.get_discord_user(current.page.owner_id)

        return create_page_embed(
            page=current.page,
            collect=current.collection,
            page_image=current.image,
            total_pages=len(self.gallery),
            original_owner=org_owner,
            hide_stats=current.page.owner_id is None
        )

    def update_buttons(self):

        self.jump_back.disabled = self.index == 0
        self.previous.disabled = self.index == 0

        self.next.disabled = self.index >= len(self.gallery) - 1
        self.jump_forward.disabled = self.index >= len(self.gallery) - 1

        self.counter.label = f"{self.index + 1} / {len(self.gallery)}"

    @discord.ui.button(
        emoji="⏪",
        style=ButtonStyle.secondary,
        row=0
    )
    async def jump_back(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.index = max(0, self.index - self.jump_size)

        self.update_buttons()

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="◀️",
        style=ButtonStyle.secondary,
        row=0
    )
    async def previous(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.index > 0:
            self.index -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
        )

    @discord.ui.button(
        label="1 / 1",
        style=ButtonStyle.secondary,
        disabled=True,
        row=0
    )
    async def counter(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):
        pass

    @discord.ui.button(
        emoji="▶️",
        style=ButtonStyle.secondary,
        row=0
    )
    async def next(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.index < len(self.gallery) - 1:
            self.index += 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="⏩",
        style=ButtonStyle.secondary,
        row=0
    )
    async def jump_forward(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        self.index = min(
            len(self.gallery) - 1,
            self.index + self.jump_size
        )

        self.update_buttons()

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
        )

    async def on_timeout(self):

        for item in self.children:
            item.disabled = True

        if self.message is not None:
            await self.message.edit(view=self)