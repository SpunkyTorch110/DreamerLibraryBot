from discord import app_commands
import discord

from utils.colours import Colours
from embeds.embed_factory import EmbedFactory

class DreamerCommandTree(app_commands.CommandTree):

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """
        This method is called on every error and reacts in different ways
        according to the error found
        """

        if isinstance(error, app_commands.CheckFailure):

            embed = EmbedFactory.create(
                title="Permission Denied",
                description="You need to be an admin to use this command.",
                colour=Colours.ERROR
            )

        else:

            import traceback
            traceback.print_exception(
                type(error),
                error,
                error.__traceback__
            )

            embed = EmbedFactory.create(
                title="Unexpected Error",
                description=f"```{type(error).__name__}: {error}```",
                colour=Colours.ERROR
            )

        if interaction.response.is_done():
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )