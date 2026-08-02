from discord.ext import commands
from discord import app_commands
import discord

from embeds.embed_factory import EmbedFactory
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

        embed = EmbedFactory.create(
            title="📚 Global Collection Progress",
            description="Claim progress of every collection of all players.\n\n",
            colour=Colours.INFO
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        lines = []

        for collection in collections:
            percentage = (
                collection.claimed_pages
                / collection.total_pages
                * 100
                if collection.total_pages
                else 0
            )

            lines.append(
                f"**{collection.collection_name}**\n"
                f"{collection.claimed_pages}/{collection.total_pages} "
                f"({percentage:.1f}%)"
            )

        embed.description += "\n\n".join(lines)

        embed.set_footer(
            text=f"{len(collections)} collections"
        )

        await interaction.followup.send(
            embed=embed
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

        embed = EmbedFactory.create(
            title="🏆 DREAMER Library Leaderboards",
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        def make_field(entries, suffix=""):
            lines = []

            for medal, entry in zip(medals, entries):
                lines.append(
                    f"{medal} **{entry.username}** — {entry.value:,}{suffix}"
                )

            return "\n".join(lines) if lines else "*No data.*"

        embed.add_field(
            name="📚 Most Pages",
            value=make_field(boards["pages"]),
            inline=True
        )

        embed.add_field(
            name="👑 First Claims",
            value=make_field(boards["claims"]),
            inline=True
        )

        embed.add_field(
            name="💰 Richest Players",
            value=make_field(boards["gold"], " GP"),
            inline=True
        )

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Library(bot))