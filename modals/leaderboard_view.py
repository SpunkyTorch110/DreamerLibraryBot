import discord

from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class LeaderboardView(discord.ui.View):

    def __init__(
            self,
            bot,
            boards
    ):
        super().__init__(timeout=300)

        self.bot = bot
        self.boards = boards

        self.current = "pages"

    def build_embed(self):

        medals = [
            "🥇",
            "🥈",
            "🥉",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣"
        ]

        titles = {
            "pages": "📚 Leaderboard for Most Pages",
            "claims": "👑 Leaderboard for First Claims",
            "gold": "💰 Leaderboard for Richest Players",
            "completion": "🏆 Leaderboard for Completionists"
        }

        descriptions = {
            "pages": (
                "The players who own the greatest total number of pages "
                "across the entire DREAMER Library."
            ),
            "claims": (
                "The players who have become the original owners of the "
                "most unique pages."
            ),
            "gold": (
                "The wealthiest collectors ranked by the amount of GP "
                "currently in their possession."
            ),
            "completion": (
                "The players who have collected the highest percentage of "
                "unique pages available in the DREAMER Library."
            )
        }

        suffixes = {
            "pages": "",
            "claims": "",
            "gold": " GP",
            "completion": "%"
        }

        entries = self.boards[self.current]

        lines = []

        for medal, entry in zip(medals, entries):

            if self.current == "completion":
                value = f"{entry.value:.1f}%"
            else:
                value = f"{entry.value:,}{suffixes[self.current]}"

            lines.append(
                f"{medal} **{entry.username}** — {value}"
            )

        embed = EmbedFactory.create(
            title=f"🏆 {titles[self.current]}",
            description=(
                    f"{descriptions[self.current]}\n\n"
                    + ("\n".join(lines) if lines else "*No data.*")
            ),
            colour=Colours.INFO
        )

        if self.bot.user:
            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.set_footer(
            text="Top 8 Players"
        )

        return embed

    @discord.ui.select(
        placeholder="Choose a leaderboard...",
        options=[
            discord.SelectOption(
                label="Most Pages",
                emoji="📚",
                value="pages"
            ),
            discord.SelectOption(
                label="First Claims",
                emoji="👑",
                value="claims"
            ),
            discord.SelectOption(
                label="Richest Players",
                emoji="💰",
                value="gold"
            ),
            discord.SelectOption(
                label="Completionists",
                emoji="🏆",
                value="completion"
            )
        ]
    )
    async def leaderboard_select(
            self,
            interaction: discord.Interaction,
            select: discord.ui.Select
    ):

        self.current = select.values[0]

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self
        )