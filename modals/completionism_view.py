import discord

import config

from embeds.embed_factory import EmbedFactory
from utils.colours import Colours


class CompletionismView(discord.ui.View):

    MILESTONES = [
        12.5,
        25.0,
        37.5,
        50.0,
        62.5,
        75.0,
        87.5,
        100.0
    ]

    def __init__(
            self,
            user: discord.User | discord.Member,
            completion: float
    ):
        super().__init__(timeout=300)

        self.user = user

        # Round completion to one decimal place.
        self.completion = round(completion, 1)

        self.message: discord.Message | None = None

        self.add_item(
            CompletionismSelect(self)
        )

    def get_next_milestone(self):

        for milestone in self.MILESTONES:

            if self.completion < milestone:
                return milestone

        return None

    def get_unlocked_milestones(self):

        return [
            milestone
            for milestone in self.MILESTONES
            if self.completion >= milestone
        ]

    def build_main_embed(self):

        next_milestone = self.get_next_milestone()

        if next_milestone is None:

            next_text = (
                "🏆 **You have reached 100% completion!**"
            )

        else:

            remaining = round(
                next_milestone - self.completion,
                1
            )

            next_text = (
                f"🌟 **Next Milestone:** {next_milestone:g}%\n"
                f"Only **{remaining:.1f}%** remaining."
            )

        embed = EmbedFactory.create(
            title="📖 Your Completionism",
            description=(
                f"Your current completion of the DREAMER Library is:\n\n"
                f"## {self.completion:.1f}%\n\n"
                f"{next_text}\n\n"
                "Select an unlocked milestone below to read its "
                "**Quote from the Book of Fate**."
            ),
            colour=Colours.INFO
        )

        embed.set_thumbnail(
            url=self.user.display_avatar.url
        )

        return embed

    def build_milestone_embed(
            self,
            level: int
    ):

        milestone = self.MILESTONES[level - 1]

        quote = config.COMPLETIONISM_QUOTES[level]

        embed = EmbedFactory.create(
            title="Quote from the Book of Fate",
            description=quote,
            colour=Colours.INFO
        )

        embed.set_footer(
            text=(
                f"Completionism Level {level} • "
                f"{milestone:g}%"
            )
        )

        return embed

    async def interaction_check(
            self,
            interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.user.id:

            await interaction.response.send_message(
                "You cannot interact with someone else's completionism.",
                ephemeral=True
            )

            return False

        return True

    async def on_timeout(self):

        for child in self.children:
            child.disabled = True

        if self.message is not None:

            try:
                await self.message.edit(
                    view=self
                )

            except discord.NotFound:
                pass


class CompletionismSelect(
        discord.ui.Select
):

    def __init__(
            self,
            parent: CompletionismView
    ):

        self.parent_view = parent

        options = []

        for index, milestone in enumerate(
                parent.MILESTONES,
                start=1
        ):

            # Don't show milestones that haven't been reached.
            if parent.completion < milestone:
                continue

            options.append(
                discord.SelectOption(
                    label=f"Level {index} — {milestone:g}%",
                    value=str(index),
                    emoji="📖"
                )
            )

        # This should never happen because the first milestone
        # is only 12.5%, but protect against an empty dropdown.
        if not options:

            options.append(
                discord.SelectOption(
                    label="No milestones unlocked",
                    value="none",
                    emoji="🔒"
                )
            )

        super().__init__(
            placeholder="Choose an unlocked level...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
            self,
            interaction: discord.Interaction
    ):

        if self.values[0] == "none":

            await interaction.response.send_message(
                "You haven't unlocked any Completionism milestones yet.",
                ephemeral=True
            )

            return

        level = int(self.values[0])

        # Extra server-side protection.
        milestone = self.parent_view.MILESTONES[level - 1]

        if self.parent_view.completion < milestone:

            await interaction.response.send_message(
                "You haven't unlocked this Completionism level yet.",
                ephemeral=True
            )

            return

        embed = self.parent_view.build_milestone_embed(
            level
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self.parent_view
        )