import discord

import config
from embeds.embed_factory import EmbedFactory
from exceptions.insufficient_gold import InsufficientGold
from exceptions.upgrade_already_purchased import UpgradeAlreadyPurchased
from utils.colours import Colours

class UpgradeConfirmationView(discord.ui.View):

    def __init__(
            self,
            bot,
            user: discord.User | discord.Member,
            upgrade: str,
            upgrade_name: str,
            cost: int,
            description: str,
            current_gold: int
    ):
        super().__init__(timeout=300)

        self.bot = bot
        self.user = user

        self.upgrade = upgrade
        self.upgrade_name = upgrade_name
        self.cost = cost
        self.description = description
        self.current_gold = current_gold

        self.finished = False
        self.message: discord.Message | None = None

    def build_embed(self):

        remaining_after_purchase = self.current_gold - self.cost

        embed = EmbedFactory.create(
            title=f"✨ Purchase {self.upgrade_name}?",
            description=(
                f"{self.description}\n\n"
                f"💰 **Cost:** {self.cost:,} GP\n"
                f"💰 **Your GP:** {self.current_gold:,} GP\n"
                f"💰 **After Purchase:** "
                f"{max(remaining_after_purchase, 0):,} GP\n\n"
                "Do you want to purchase this upgrade?"
            ),
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.user.display_avatar.url
        )

        embed.set_footer(
            text="This upgrade is permanent."
        )

        return embed

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.user.id:

            await interaction.response.send_message(
                "You cannot interact with someone else's upgrade.",
                ephemeral=True
            )

            return False

        return True

    def disable_buttons(self):

        for child in self.children:
            child.disabled = True

    @discord.ui.button(
        label="Buy",
        emoji="💰",
        style=discord.ButtonStyle.success
    )
    async def buy(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.finished:
            return

        #
        # Acknowledge the button immediately.
        #

        await interaction.response.defer()

        try:

            cost, remaining_gold = (
                await self.bot.player_service.purchase_upgrade(
                    self.user,
                    self.upgrade
                )
            )

        except UpgradeAlreadyPurchased:

            self.finished = True
            self.disable_buttons()

            embed = EmbedFactory.create(
                title="⚠️ Upgrade Already Purchased",
                description=(
                    f"You already own the **{self.upgrade_name}** upgrade."
                ),
                colour=Colours.WARNING
            )

            await interaction.edit_original_response(
                embed=embed,
                view=self
            )

            return

        except InsufficientGold:

            self.finished = True
            self.disable_buttons()

            embed = EmbedFactory.create(
                title="💰 Not Enough GP",
                description=(
                    f"You don't have enough GP to purchase "
                    f"the **{self.upgrade_name}** upgrade.\n\n"
                    f"Cost: **{self.cost:,} GP**"
                ),
                colour=Colours.WARNING
            )

            await interaction.edit_original_response(
                embed=embed,
                view=self
            )

            return

        self.finished = True
        self.disable_buttons()

        if self.upgrade == "roll":

            success_description = (
                f"Your roll recharge time is now "
                f"**{config.ROLL_RECHARGE_UPGRADED.total_seconds() / 3600:g} hours**."
            )

        elif self.upgrade == "claim":

            success_description = (
                f"Your claim recharge time is now "
                f"**{config.CLAIM_RECHARGE_UPGRADED.total_seconds() / 3600:g} hours**."
            )

        elif self.upgrade == "roll_capacity":

            success_description = (
                f"Your maximum rolls are now "
                f"**{config.MAX_ROLLS_UPGRADED}**."
            )

        else:

            success_description = (
                f"Your maximum claims are now "
                f"**{config.MAX_CLAIMS_UPGRADED}**."
            )

        embed = EmbedFactory.create(
            title=f"✨ {self.upgrade_name} Purchased!",
            description=(
                f"{success_description}\n\n"
                f"💰 **Paid:** {cost:,} GP\n"
                f"💰 **Remaining:** {remaining_gold:,} GP"
            ),
            colour=Colours.SUCCESS
        )

        embed.set_thumbnail(
            url=self.user.display_avatar.url
        )

        await interaction.edit_original_response(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Cancel",
        emoji="❌",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        if self.finished:
            return

        self.finished = True
        self.disable_buttons()

        embed = EmbedFactory.create(
            title="Upgrade Cancelled",
            description=(
                f"You decided not to purchase the "
                f"**{self.upgrade_name}** upgrade."
            ),
            colour=Colours.INFO
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    async def on_timeout(self):

        self.finished = True
        self.disable_buttons()

        if self.message is not None:

            try:

                await self.message.edit(
                    view=self
                )

            except discord.NotFound:
                pass