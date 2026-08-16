import discord
from discord import app_commands
from discord.ext import commands

from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class PatchNotes(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(
        name="patchnotes",
        description="Shows the latest DREAMER Library patch notes."
    )
    async def patchnotes(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        embed = EmbedFactory.create(
            title="📜 DREAMER Library — Patch Notes v1.1",
            description=(
                "**Version v1.1**\n\n"
                "A new update bringing new collection, progression, "
                "economy and quality-of-life features.\n\n"

                "📚 **Collection & Gallery**\n"
                "• Added a `/player gallery` command that shows the "
                "Pages of the Player in a gallery form.\n"
                "• Added a `/pages collections (name)` command to show "
                "the Pages of a certain collection.\n"
                "• Added a `/player collections (name)` command to show "
                "the Pages a player has of a certain collection.\n\n"

                "🏆 **Leaderboards**\n"
                "• Added a new Leaderboard for Completionism.\n"
                "• Leaderboard now shows **Top 8** instead of **Top 5**.\n\n"

                "💰 **Economy**\n"
                "• When you sell a Page, the total amount of GP the "
                "Player has now shows up.\n"
                "• Added a `/player upgrade` command that allows "
                "players to use GP to buy permanent upgrades.\n"
                "• Added a `/shop` command that allows players to buy "
                "Rolls and Claims using GP.\n\n"

                "📖 **Book of Fate**\n"
                "• Added a `/player completionism` command that shows "
                "the player's progress in completing the library and "
                "lets the player unlock Chapters of the Book of Fate "
                "according to their progression percentage.\n\n"

                "🛠️ **Quality of Life**\n"
                "• Added a `/patchnotes` command that shows the patch notes.\n"
                "• Updated the `/help` command to show new commands."
            ),
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        embed.set_footer(
            text="DREAMER Library • Version v1.1"
        )

        await interaction.followup.send(
            embed=embed
        )

async def setup(bot):
    await bot.add_cog(
        PatchNotes(bot)
    )