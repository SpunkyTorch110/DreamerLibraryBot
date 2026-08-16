import discord
from discord import app_commands
from discord.ext import commands

from modals.shop_view import ShopView


class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="shop",
        description="Purchase Rolls and Claims with GP."
    )
    async def shop(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        player = await self.bot.player_service.get_active_player(
            interaction.user
        )

        max_rolls = await self.bot.player_service.get_max_rolls(
            player.discord_id
        )

        max_claims = await self.bot.player_service.get_max_claims(
            player.discord_id
        )

        view = ShopView(
            bot=self.bot,
            user=interaction.user,

            current_gold=player.gold,

            current_rolls=player.rolls_remaining,
            max_rolls=max_rolls,

            current_claims=player.claims_remaining,
            max_claims=max_claims
        )

        message = await interaction.followup.send(
            embed=view.build_embed(),
            view=view,
            wait=True
        )

        view.message = message

async def setup(bot):
    await bot.add_cog(
        Shop(bot)
    )