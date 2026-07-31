import asyncio
import discord
from discord.ext import commands

import config
from db.database import Database


class DreamerLibraryBot(commands.Bot):

    def __init__(self):
        self.database = None

        intents = discord.Intents.default()

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents
        )

    async def setup_hook(self):
        print("Loading extensions...")

        self.database = Database(config.DATABASE)
        await self.database.initialize()

        await self.load_extension("cogs.ping")

        print("Syncing slash commands...")
        await self.tree.sync()

        print("DreamerLibraryBot is ready.")

    async def on_ready(self):
        print(f"Logged in as {self.user}")


async def main():
    bot = DreamerLibraryBot()

    async with bot:
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())