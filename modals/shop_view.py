import discord

import config
from embeds.embed_factory import EmbedFactory
from modals.shop_purchase_view import ShopPurchaseView
from utils.colours import Colours


class ShopView(discord.ui.View):

    def __init__(
            self,
            bot,
            user: discord.User | discord.Member,
            current_gold: int,
            max_rolls: int,
            current_rolls: int,
            max_claims: int,
            current_claims: int
    ):
        super().__init__(timeout=300)

        self.bot = bot
        self.user = user

        self.current_gold = current_gold

        self.max_rolls = max_rolls
        self.current_rolls = current_rolls

        self.max_claims = max_claims
        self.current_claims = current_claims

        self.message: discord.Message | None = None

        self.update_buttons()

    def build_embed(self):

        embed = EmbedFactory.create(
            title="🛒 DREAMER Shop",
            description=(
                "Purchase additional Rolls and Claims with GP.\n\n"

                f"💰 **Your GP:** `{self.current_gold:,} GP`\n\n"

                f"🎲 **Roll**\n"
                f"Purchase 1 additional roll for "
                f"**{config.ROLL_SHOP_PRICE:,} GP**.\n"
                f"Current: `{self.current_rolls}/{self.max_rolls}`\n\n"

                f"👑 **Claim**\n"
                f"Purchase 1 additional claim for "
                f"**{config.CLAIM_SHOP_PRICE:,} GP**.\n"
                f"Current: `{self.current_claims}/{self.max_claims}`"
            ),
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.user.display_avatar.url
        )

        embed.set_footer(
            text="Purchased resources are added immediately."
        )

        return embed

    def update_buttons(self):

        self.buy_roll.disabled = (
            self.current_rolls >= self.max_rolls
            or self.current_gold < config.ROLL_SHOP_PRICE
        )

        self.buy_claim.disabled = (
            self.current_claims >= self.max_claims
            or self.current_gold < config.CLAIM_SHOP_PRICE
        )

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.user.id:

            await interaction.response.send_message(
                "You cannot interact with someone else's shop.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="Buy Roll",
        emoji="🎲",
        style=discord.ButtonStyle.primary
    )
    async def buy_roll(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        view = ShopPurchaseView(
            bot=self.bot,
            user=self.user,
            resource="roll",
            price=config.ROLL_SHOP_PRICE
        )

        await interaction.response.send_message(
            embed=view.build_embed(),
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Buy Claim",
        emoji="👑",
        style=discord.ButtonStyle.primary
    )
    async def buy_claim(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
    ):

        view = ShopPurchaseView(
            bot=self.bot,
            user=self.user,
            resource="claim",
            price=config.CLAIM_SHOP_PRICE
        )

        await interaction.response.send_message(
            embed=view.build_embed(),
            view=view,
            ephemeral=True
        )