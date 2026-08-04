import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

import config
from embeds.embed_factory import EmbedFactory
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

    @player.command(
        name="timers",
        description="Shows your current rolls, claims and cooldowns."
    )
    async def timers(
            self,
            interaction: discord.Interaction
    ):

        await interaction.response.defer(
        )

        player = await self.bot.player_service.get_active_player(
            interaction.user
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
            text=f"Rolls regenerate every {config.ROLL_RECHARGE} hours • Claims regenerate every {config.CLAIM_RECHARGE} hours"
        )

        await interaction.followup.send(
            embed=embed,
        )

async def setup(bot):
    await bot.add_cog(
        Player(bot)
    )