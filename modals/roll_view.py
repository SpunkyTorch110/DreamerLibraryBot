import discord

import config
from embeds.embed_factory import EmbedFactory
from embeds.page_layout import create_page_embed
from exceptions.no_claims_remaining import NoClaimsRemaining
from models.schema.page import Page
from utils.colours import Colours


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

        self.update_buttons()

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

    def update_buttons(self):

        #
        # Disable claim if the player has no claims available.
        #

        self.claim.disabled = (
                self.result.claims_remaining <= 0
        )

    async def build_embed(self):

        page = await self.bot.page_repository.get(
            self.result.page.id
        )

        owned_amount = await self.bot.inventory_repository.get_amount(
            self.result.player.discord_id,
            page.id
        )

        return create_page_embed(
            page=page,
            collect=self.result.collection,
            page_image=self.result.image,
            total_pages=await self.bot.page_service.get_total_pages(),
            original_owner=await self.bot.player_service.get_discord_user(
                page.owner_id
            ),
            hide_stats=page.owner_id is None,
            owned_amount=owned_amount
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

        try:
            await self.bot.roll_service.claim(
                self.result.player.discord_id,
                self.result.page.id
            )

        except NoClaimsRemaining:

            embed = EmbedFactory.create(
                title="No Claims Remaining",
                description=(
                    "You don't have any claims remaining.\n"
                    "Use **/player timers** to see when your next claim recharges."
                ),
                colour=Colours.WARNING
            )

            await interaction.response.send_message(
                embed=embed,
            )

            return

        self.finished = True

        for child in self.children:
            child.disabled = True

        #
        # Disable the buttons on the original roll message.
        #

        await interaction.response.edit_message(
            embed=await self.build_embed(),
            view=None
        )

        #
        # Get updated completionism percentage.
        #

        completion = await self.bot.player_service.get_completion_percentage(
            interaction.user
        )

        #
        # Announce the claim.
        #

        embed = EmbedFactory.create(
            title=(
                f"📚 {interaction.user.display_name} claimed "
                f"**{self.result.page.name}**!"
            ),
            description=(
                f"**{self.result.page.name}** has been added to "
                f"{interaction.user.display_name}'s library.\n\n"
                f"📖 **Completionism:** `{completion:.1f}%`"
            ),
            colour=Colours.SUCCESS
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        await interaction.followup.send(
            embed=embed
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

        gold, total_gold = await self.bot.roll_service.sell(
            self.result.player.discord_id,
            self.result.page.rarity
        )

        self.finished = True

        for child in self.children:
            child.disabled = True

        embed = EmbedFactory.create(
            title=(
                f"💰 {interaction.user.display_name} sold "
                f"**{self.result.page.name}**"
            ),
            description=(
                f"You sold **{self.result.page.name}** "
                f"for a total of **{gold} GP**.\n\n"
                f"💰 Your current balance is **{total_gold:,} GP**."
            ),
            colour=Colours.SUCCESS
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
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