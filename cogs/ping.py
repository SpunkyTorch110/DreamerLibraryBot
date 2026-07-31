from discord import app_commands
from discord.ext import commands

from utils.embeds import EmbedFactory
from utils.colours import ping_colour


class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Shows the bot latency."
    )
    async def ping(self, interaction):

        latency = round(self.bot.latency * 1000)

        embed = EmbedFactory.create(
            title="Pong!",
            description=f"The current bot latency is **{latency} ms**",
            colour=ping_colour(latency)
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Ping(bot))