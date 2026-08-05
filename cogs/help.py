import discord
from discord import app_commands
from discord.ext import commands

from modals.help_view import HelpView


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Shows information about the Bot and how to play!"
    )
    async def help(
            self,
            interaction: discord.Interaction
    ):

        await interaction.response.defer()

        view = HelpView(
            bot=self.bot
        )

        await interaction.followup.send(
            embed=view.build_embed(),
            view=view
        )


async def setup(bot):
    await bot.add_cog(
        Help(bot)
    )