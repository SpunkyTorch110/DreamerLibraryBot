from discord import app_commands
from discord.ext import commands
import discord
import traceback

from embeds.embed_factory import EmbedFactory
from exceptions.no_claims_remaining import NoClaimsRemaining
from exceptions.no_rolls_remaining import NoRollsRemaining
from utils.colours import Colours


class DreamerCommandTree(app_commands.CommandTree):

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):

        # Discord wraps exceptions raised inside commands.
        if isinstance(error, app_commands.CommandInvokeError):
            original = error.original
        else:
            original = error

        # ------------------------------
        # Permission denied
        # ------------------------------
        if isinstance(error, app_commands.CheckFailure):

            embed = EmbedFactory.create(
                title="Permission Denied",
                description="You do not have permission to use this command.",
                colour=Colours.ERROR
            )

        # ------------------------------
        # Invalid enum / transformer
        # ------------------------------
        elif isinstance(error, app_commands.TransformerError):

            embed = EmbedFactory.create(
                title="Invalid Value",
                description="One or more of the provided values are invalid.",
                colour=Colours.ERROR
            )

        # ------------------------------
        # Wrong command usage
        # ------------------------------
        elif isinstance(error, app_commands.CommandSignatureMismatch):

            embed = EmbedFactory.create(
                title="Invalid Command",
                description="The command parameters are invalid.",
                colour=Colours.ERROR
            )

        # ------------------------------
        # Validation errors from services
        # ------------------------------
        elif isinstance(original, ValueError):

            embed = EmbedFactory.create(
                title="Invalid Operation",
                description=str(original),
                colour=Colours.ERROR
            )

        # ------------------------------
        # No rolls remaining
        # ------------------------------
        elif isinstance(original, NoRollsRemaining):

            embed = EmbedFactory.create(
                title="No Rolls Remaining",
                description=(
                    "You don't have any rolls remaining.\n"
                    "Use **/player timers** to check when your next rolls recharge."
                ),
                colour=Colours.WARNING
            )

        # ------------------------------
        # No claims remaining
        # ------------------------------
        elif isinstance(original, NoClaimsRemaining):

            embed = EmbedFactory.create(
                title="No Claims Remaining",
                description=(
                    "You don't have any claims remaining.\n"
                    "Use **/player timers** to check when your next claim recharges."
                ),
                colour=Colours.WARNING
            )

        # ------------------------------
        # Cooldowns (future)
        # ------------------------------
        elif isinstance(error, commands.CommandOnCooldown):

            embed = EmbedFactory.create(
                title="Slow Down",
                description=f"Try again in {error.retry_after:.1f} seconds.",
                colour=Colours.WARNING
            )

        # ------------------------------
        # Everything else
        # ------------------------------
        else:

            traceback.print_exception(
                type(original),
                original,
                original.__traceback__
            )

            embed = EmbedFactory.create(
                title="Unexpected Error",
                description=f"```{type(original).__name__}: {original}```",
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