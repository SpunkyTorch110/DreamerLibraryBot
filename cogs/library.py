from discord.ext import commands
from discord import app_commands
import discord

from embeds.embed_factory import EmbedFactory
from modals.leaderboard_view import LeaderboardView
from modals.library_collections_view import LibraryCollectionsView
from utils.colours import Colours


class Library(commands.Cog):

    library = app_commands.Group(
        name="library",
        description="Commands related to the DREAMER Library."
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @library.command(
        name="info",
        description="Shows general information about the DREAMER Library."
    )
    async def info(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        info = await self.bot.library_service.get_library_info()

        embed = EmbedFactory.create(
            title="📚 DREAMER Library",
            description="Current overall statistics of the library.",
            colour=Colours.INFO
        )

        if self.bot.user is not None:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.add_field(
            name="📖 Library",
            value=(
                f"**Total Pages:** {info.total_pages:,}\n"
                f"**Discovered:** {info.discovered_pages:,} ({info.discovery_percentage:.1f}%)\n"
                f"**Claimed:** {info.claimed_pages:,} ({info.claim_percentage:.1f}%)\n"
                f"**Collections:** {info.total_collections:,}"
            ),
            inline=True
        )

        embed.add_field(
            name="👥 Community",
            value=(
                f"**Players:** {info.total_players:,}\n"
                f"**Copies Owned:** {info.total_copies:,}\n"
                f"**Average Copies/Page:** {info.average_copies_per_page:.2f}\n"
                f"**Total Gold:** {info.total_gold:,} GP"
            ),
            inline=True
        )

        embed.set_footer(
            text="The Library grows with its players."
        )

        await interaction.followup.send(
            embed=embed
        )

    @library.command(
        name="collections",
        description="Shows the progress of every collection in the Library."
    )
    async def collections(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        collections = await self.bot.library_service.get_collection_progress()

        view = LibraryCollectionsView(
            bot=self.bot,
            collections=collections
        )

        await interaction.followup.send(
            embed=view.build_embed(),
            view=view
        )

    @library.command(
        name="leaderboard",
        description="Shows the Player Ranking Leaderboards."
    )
    async def leaderboard(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        boards = await self.bot.library_service.get_leaderboards()

        view = LeaderboardView(
            bot=self.bot,
            boards=boards
        )

        await interaction.followup.send(
            embed=view.build_embed(),
            view=view
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Library(bot))