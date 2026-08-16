import discord

from embeds.embed_factory import EmbedFactory
from exceptions.insufficient_gold import InsufficientGold
from exceptions.resource_at_max import ResourceAtMax
from utils.colours import Colours


class ShopPurchaseView(discord.ui.View):

    def __init__(
            self,
            bot,
            user: discord.User | discord.Member,
            resource: str,
            price: int
    ):
        super().__init__(timeout=60)

        self.bot = bot
        self.user = user

        self.resource = resource
        self.price = price

        self.finished = False

        self.message: discord.Message | None = None

    def build_embed(self):

        if self.resource == "roll":

            name = "Roll"
            emoji = "🎲"

        else:

            name = "Claim"
            emoji = "👑"

        embed = EmbedFactory.create(
            title=f"{emoji} Purchase {name}?",
            description=(
                f"Are you sure you want to purchase "
                f"**1 {name}**?\n\n"
                f"💰 **Cost:** {self.price:,} GP"
            ),
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.user.display_avatar.url
        )

        return embed

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.user.id:

            await interaction.response.send_message(
                "You cannot interact with someone else's purchase.",
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

        await interaction.response.defer()

        try:

            if self.resource == "roll":

                cost, remaining_gold = (
                    await self.bot.player_service.buy_roll(
                        self.user
                    )
                )

                resource_name = "Roll"
                emoji = "🎲"

            else:

                cost, remaining_gold = (
                    await self.bot.player_service.buy_claim(
                        self.user
                    )
                )

                resource_name = "Claim"
                emoji = "👑"

        except ResourceAtMax:

            self.finished = True
            self.disable_buttons()

            embed = EmbedFactory.create(
                title="⚠️ Already At Maximum",
                description=(
                    f"You already have the maximum number "
                    f"of {resource_name.lower()}s."
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
                    f"this {resource_name.lower()}."
                ),
                colour=Colours.WARNING
            )

            await interaction.edit_original_response(
                embed=embed,
                view=self
            )

            return

        except Exception as error:

            import traceback

            traceback.print_exc()

            self.finished = True
            self.disable_buttons()

            embed = EmbedFactory.create(
                title="❌ Shop Error",
                description=(
                    "Something went wrong while processing "
                    "your purchase."
                ),
                colour=Colours.ERROR
            )

            await interaction.edit_original_response(
                embed=embed,
                view=self
            )

            return

        self.finished = True
        self.disable_buttons()

        embed = EmbedFactory.create(
            title=f"{emoji} {resource_name} Purchased!",
            description=(
                f"You purchased **1 {resource_name.lower()}** "
                f"for **{cost:,} GP**.\n\n"
                f"💰 **Remaining GP:** "
                f"{remaining_gold:,} GP"
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
            title="Purchase Cancelled",
            description="You didn't purchase anything.",
            colour=Colours.INFO
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )