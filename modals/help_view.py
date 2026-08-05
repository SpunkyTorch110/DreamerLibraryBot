import discord

from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class HelpView(discord.ui.View):

    def __init__(
            self,
            bot
    ):
        super().__init__(timeout=300)

        self.bot = bot

        self.page = "overview"

    def build_embed(self):

        embed = EmbedFactory.create(
            colour=Colours.INFO
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        match self.page:

            #
            # Overview
            #

            case "overview":

                embed.title = "📖 DREAMER Library"

                embed.description = (
                    "Welcome to **DREAMER Library**, a collectible page game "
                    "where every player works together to discover every page. "
                    "This bot is based on the characters of my D&D Universe / Stories and have the following content:"
                    "\n\n"
                    
                    "- **D&D DREAMER** (Old + New)\n"
                    "- **D&D ToG** (Fully)\n"
                    "- Later on the sequel to DREAMER (E.D)\n"

                    "## Start Rolling!\n"

                    "Your journey begins with **/roll**.\n\n"

                    "After rolling you may:\n"
                    "📚 **Claim** the page to add it to your collection.\n"
                    "💰 **Sell** the page for GP.\n\n"

                    "Every newly rolled page becomes permanently discovered "
                    "for everyone.\n"

                    "## ⭐ Roll Chances\n"

                    "⭐ Common — **50%**\n"
                    "⭐⭐ Rare — **35%**\n"
                    "⭐⭐⭐ Legendary — **15%**"
                )

                embed.set_footer(
                    text="Use the dropdown below to browse all commands."
                )

            #
            # General
            #

            case "general":

                embed.title = "📡 General Commands"

                embed.description = (
                    "General utility commands available in DREAMER Library."
                )

                embed.add_field(
                    name="/ping",
                    value=(
                        "Displays the bot latency and checks "
                        "whether the bot is online."
                    ),
                    inline=False
                )

                embed.add_field(
                    name="/bot",
                    value=(
                        "Displays information about the bot. "
                    ),
                    inline=False
                )

            #
            # Library
            #

            case "library":

                embed.title = "📚 Library Commands"

                embed.description = (
                    "Commands related to the global DREAMER Library."
                )

                embed.add_field(
                    name="/library info",
                    value="Shows overall Global Library statistics.",
                    inline=False
                )

                embed.add_field(
                    name="/library collections",
                    value="Displays the progress of every collection globally.",
                    inline=False
                )

                embed.add_field(
                    name="/library leaderboard",
                    value="Shows the player leaderboards.",
                    inline=False
                )

            #
            # Pages
            #

            case "pages":

                embed.title = "📄 Page Commands"

                embed.description = (
                    "Commands related to browsing Library pages."
                )

                embed.add_field(
                    name="/pages search",
                    value="Search for a page by name or alias.",
                    inline=False
                )

                embed.add_field(
                    name="/pages list",
                    value="Lists every page in the Library.",
                    inline=False
                )

                embed.add_field(
                    name="/pages gallery",
                    value="Browse every page one by one in a gallery.",
                    inline=False
                )

            #
            # Player
            #

            case "player":

                embed.title = "👤 Player Commands"

                embed.description = (
                    "Commands related to your personal profile."
                )

                embed.add_field(
                    name="/player profile",
                    value="Shows your player profile.",
                    inline=False
                )

                embed.add_field(
                    name="/player pages",
                    value="Displays every page you own.",
                    inline=False
                )

                embed.add_field(
                    name="/player collections",
                    value="Shows your collection completion.",
                    inline=False
                )

                embed.add_field(
                    name="/player check",
                    value="View another player's profile.",
                    inline=False
                )

                embed.add_field(
                    name="/player timers",
                    value="Shows your remaining Rolls and Claims.",
                    inline=False
                )

        return embed

    @discord.ui.select(
        placeholder="Select a help category...",
        options=[
            discord.SelectOption(
                label="Overview",
                emoji="📖",
                value="overview"
            ),
            discord.SelectOption(
                label="General Commands",
                emoji="📡",
                value="general"
            ),
            discord.SelectOption(
                label="Library Commands",
                emoji="📚",
                value="library"
            ),
            discord.SelectOption(
                label="Page Commands",
                emoji="📄",
                value="pages"
            ),
            discord.SelectOption(
                label="Player Commands",
                emoji="👤",
                value="player"
            ),
        ]
    )
    async def select_page(
            self,
            interaction: discord.Interaction,
            select: discord.ui.Select
    ):

        self.page = select.values[0]

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )