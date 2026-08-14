import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

import config
from embeds.embed_factory import EmbedFactory
from modals.collection_progress_view import CollectionProgressView
from modals.player_gallery_view import PlayerGalleryView
from modals.player_pages_view import PlayerPagesView
from models.player_profile_view import PlayerProfileView
from utils.colours import Colours


class Player(commands.Cog):

    player = app_commands.Group(
        name="player",
        description="Commands related to your player."
    )

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def format_timestamp(
            date: datetime | None
    ) -> str:
        if date is None:
            return "✅ Ready!"

        return f"<t:{int(date.timestamp())}:R>"

    def create_profile_embed(
            self,
            member: discord.User | discord.Member,
            profile: PlayerProfileView
    ) -> discord.Embed:
        player = profile.player

        embed = EmbedFactory.create(
            title=f"📖 {member.display_name}'s Profile",
            description="See the profile and Book Of Fate of this user.",
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="📚 Collection",
            value=(
                f"**Pages:** {profile.total_pages}\n"
                f"**Unique:** {profile.unique_pages}\n"
                f"**First Claims:** {profile.first_claims}\n"
                f"**Completion:** "
                f"{profile.unique_pages}/{profile.total_library_pages} "
                f"({profile.completion_percentage:.1f}%)"
            ),
            inline=True
        )

        embed.add_field(
            name="💰 Resources",
            value=(
                f"**Gold:** {player.gold:,} GP\n"
                f"**Rolls:** "
                f"{player.rolls_remaining}/{config.MAX_ROLLS}\n"
                f"**Claims:** "
                f"{player.claims_remaining}/{config.MAX_CLAIMS}"
            ),
            inline=True
        )

        embed.add_field(
            name="👤 Account",
            value=(
                f"**Username:** {player.username}\n"
                f"**Created:** "
                f"<t:{int(player.created_at.timestamp())}:D>"
            ),
            inline=False
        )

        embed.set_footer(
            text="Keep growing your own Book of Fate!"
        )

        return embed

    @player.command(
        name="timers",
        description="Shows your current rolls, claims and cooldowns."
    )
    async def timers(
            self,
            interaction: discord.Interaction
    ):

        await interaction.response.defer()

        player = await self.bot.player_service.get_active_player(
            interaction.user
        )

        roll_recharge, claim_recharge = (
            await self.bot.player_service.get_player_recharge_times(
                player.discord_id
            )
        )

        embed = EmbedFactory.create(
            title="⏳ Your Timers",
            description="Current recharge status.",
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.add_field(
            name="🎲 Rolls",
            value=(
                f"**Remaining:** "
                f"`{player.rolls_remaining}/{config.MAX_ROLLS}`\n"
                f"**Next Roll:** "
                f"{self.format_timestamp(player.next_roll_at)}"
            ),
            inline=True
        )

        embed.add_field(
            name="👑 Claims",
            value=(
                f"**Remaining:** "
                f"`{player.claims_remaining}/{config.MAX_CLAIMS}`\n"
                f"**Next Claim:** "
                f"{self.format_timestamp(player.next_claim_at)}"
            ),
            inline=True
        )

        embed.set_footer(
            text=(
                f"Rolls regenerate every {roll_recharge.total_seconds() / 3600} hours "
                f"• Claims regenerate every {claim_recharge.total_seconds() / 3600} hours"
            )
        )

        await interaction.followup.send(
            embed=embed
        )

    @player.command(
        name="profile",
        description="Shows your Library Player profile."
    )
    async def profile(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        profile = await self.bot.player_service.get_profile(
            interaction.user
        )

        await interaction.followup.send(
            embed=self.create_profile_embed(
                interaction.user,
                profile
            )
        )

    @player.command(
        name="check",
        description="Shows another player's profile."
    )
    async def check(
            self,
            interaction: discord.Interaction,
            member: discord.Member
    ):
        await interaction.response.defer()

        profile = await self.bot.player_service.get_profile_if_exists(
            member
        )

        if profile is None:
            embed = EmbedFactory.create(
                title="No Profile Found",
                description=(
                    f"{member.display_name} does not have a profile yet.\n"
                    "Encourage them to start playing!"
                ),
                colour=Colours.INFO
            )

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

            embed.set_footer(
                text="Everyone should follow their Fate."
            )

            await interaction.followup.send(
                embed=embed
            )

            return

        await interaction.followup.send(
            embed=self.create_profile_embed(
                member,
                profile
            )
        )

    @player.command(
        name="collections",
        description="Shows your player progress in every collection."
    )
    async def collections(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        progress = await self.bot.player_service.get_collection_progress(
            interaction.user
        )

        view = CollectionProgressView(
            user=interaction.user,
            progress=progress
        )

        await interaction.followup.send(
            embed=view.build_embed(),
            view=view
        )

    @player.command(
        name="pages",
        description="Shows the pages in your personal book."
    )
    @app_commands.describe(
        collection="Optional collection to filter your pages by."
    )
    async def pages(
            self,
            interaction: discord.Interaction,
            collection: str | None = None
    ):
        await interaction.response.defer()

        collection_id = None
        collection_name = None

        #
        # If a collection was specified, find it.
        #

        if collection is not None:

            found_collection = await self.bot.collection_repository.find_by_name(
                collection
            )

            if found_collection is None:
                embed = EmbedFactory.create(
                    title="📚 Collection Not Found",
                    description=(
                        f"No collection named **{collection}** was found."
                    ),
                    colour=Colours.WARNING
                )

                await interaction.followup.send(
                    embed=embed
                )

                return

            collection_id = found_collection.id
            collection_name = found_collection.name

        #
        # Create the View.
        #

        view = PlayerPagesView(
            bot=self.bot,
            user=interaction.user,
            collection_id=collection_id,
            collection_name=collection_name
        )

        await view.load_page()

        #
        # No pages in the selected collection.
        #

        if view.total_pages == 0:

            if collection_name is not None:

                description = (
                    f"You don't have any pages from "
                    f"**{collection_name}** yet."
                )

            else:

                description = (
                    "You don't have any pages in your personal book yet.\n\n"
                    "Use **/roll** to start collecting pages!"
                )

            embed = EmbedFactory.create(
                title="📖 Your Pages",
                description=description,
                colour=Colours.INFO
            )

            embed.set_thumbnail(
                url=interaction.user.display_avatar.url
            )

            await interaction.followup.send(
                embed=embed
            )

            return

        await interaction.followup.send(
            embed=view.build_embed(),
            view=view
        )

    @player.command(
        name="gallery",
        description="Browse all pages currently in your collection."
    )
    async def gallery(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        entries, total = await self.bot.player_service.get_player_gallery_entries(
            interaction.user,
            limit=1,
            offset=0
        )

        if total == 0:
            embed = EmbedFactory.create(
                title="📚 Your Gallery",
                description=(
                    "You don't have any pages in your collection yet.\n\n"
                    "Use **/roll** to discover and collect your first page!"
                ),
                colour=Colours.INFO
            )

            embed.set_thumbnail(
                url=interaction.user.display_avatar.url
            )

            await interaction.followup.send(
                embed=embed
            )

            return

        view = PlayerGalleryView(
            bot=self.bot,
            player=interaction.user,
            total=total,
            entry=entries[0]
        )

        await interaction.followup.send(
            embed=await view.build_embed(),
            view=view
        )

async def setup(bot):
    await bot.add_cog(
        Player(bot)
    )