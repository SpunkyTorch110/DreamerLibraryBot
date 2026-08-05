import discord

import config
from embeds.page_layout import create_page_embed


class RollView(discord.ui.View):

    def __init__(
            self,
            bot,
            result
    ):
        super().__init__(timeout=120)

        self.bot = bot
        self.result = result

        self.finished = False

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ) -> bool:

        if (
                interaction.user.id
                != self.result.player.discord_id
        ):

            await interaction.response.send_message(
                "Only the player who rolled this page can interact with it.",
                ephemeral=True
            )

            return False

        return True

    async def build_embed(self):

        return create_page_embed(
            page=self.result.page,
            collect=self.result.collection,
            page_image=self.result.image,
            total_pages=await self.bot.page_service.get_total_pages(),
            hide_stats=self.result.page.owner_id is None
        )

    @discord.ui.button(
        label="Claim",
        emoji="📚",
        style=discord.ButtonStyle.success
    )
    async def claim(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.finished:
            return

        await self.bot.roll_service.claim(
            self.result.player,
            self.result.page
        )

        self.result.page.owner_id = (
            self.result.player.discord_id
        )

        self.finished = True

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="💰",
        style=discord.ButtonStyle.secondary
    )
    async def sell(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.finished:
            return

        gold = await self.bot.roll_service.sell(
            self.result.player,
            self.result.page.rarity
        )

        self.finished = True

        for child in self.children:
            child.disabled = True

        embed = await self.build_embed()

        embed.add_field(
            name="Sold",
            value=f"You received **{gold} GP**.",
            inline=False
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    async def on_timeout(self):

        if self.finished:
            return

        self.finished = True

        for child in self.children:
            child.disabled = True

        # Disable buttons on the original message
        if hasattr(self, "message"):
            await self.message.edit(view=self)