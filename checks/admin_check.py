import discord
from discord import app_commands

import config

# decorator used to check if the command sender is an admin
def is_admin():

    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id in config.ADMIN_IDS

    return app_commands.check(predicate)