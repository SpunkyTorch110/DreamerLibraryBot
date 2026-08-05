import discord
from discord import app_commands
from discord.ext import commands

import config
from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class BotCog(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(
        name="bot",
        description="Shows information about the DREAMER Library bot."
    )
    async def bot(
            self,
            interaction: discord.Interaction
    ):
        embed = EmbedFactory.create(
            title="📖 Welcome to DREAMER Library v1.0",
            description=(
                f"This bot was developed by {config.BOT_CREATOR} to let players collect, "
                "trade, and discover pages from my **D&D universe and stories**.\n\n"
                "If you'd like to add DREAMER Library to your own Discord server, "
                "feel free to ask me as I may make it available!\n\n"

                "**✨ Available in v1.0**\n"
                "• 📚 Collect and discover unique Pages\n"
                "• 📖 Collection tracking\n"
                "• 👤 Player profiles and inventories\n"
                "• 🎲 Roll, 📚 Claim, and 💰 Sell Pages\n"
                "• 🏆 Global leaderboards\n"
                "• 📄 Library browser and gallery\n"
                "• And much more!\n\n"

                "**🚀 Planned for Future Versions**\n"
                "• 🤝 Player Page Trading\n"
                "• 🎮 Mini-Games\n"
                "• 🛒 Central Market\n"
                "• ⚔️ Autobattling\n"
                "• 👥 Team Formation\n"
                "• ⭐ Favorite Pages\n"
                "• 🎭 Collection Showcases & Flexing\n"
                "• 📈 Market Upgrades\n"
                "• 💎 Soul Upgrades\n"
                "• 📚 Hundreds of New Pages\n"
                "• ✨ Quality of Life Improvements"
            ),
            colour=Colours.INFO
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.set_footer(
            text="DREAMER Library • Version 1.0"
        )

        await interaction.response.send_message(
            embed=embed
        )

async def setup(bot):
    await bot.add_cog(
        BotCog(bot)
    )