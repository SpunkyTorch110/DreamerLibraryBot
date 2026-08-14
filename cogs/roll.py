import discord
from discord import app_commands
from discord.ext import commands

from checks.admin_check import is_admin
from modals.roll_view import RollView


class Roll(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="roll",
        description="Roll a random page."
    )
    async def roll(
            self,
            interaction: discord.Interaction
    ):

        await interaction.response.defer()

        result = await self.bot.roll_service.roll(
            interaction.user
        )

        view = RollView(
            bot=self.bot,
            result=result
        )

        await interaction.followup.send(
            embed=await view.build_embed(),
            view=view
        )


async def setup(bot):
    await bot.add_cog(
        Roll(bot)
    )