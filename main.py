import asyncio
import discord
from discord.ext import commands

import config
from bot.dreamer_command_tree import DreamerCommandTree
from db.database import Database
from db.repositories.collection_repository import CollectionRepository
from db.repositories.inventory_repository import InventoryRepository
from db.repositories.page_alias_repository import PageAliasRepository
from db.repositories.page_image_repository import PageImageRepository
from db.repositories.page_repository import PageRepository
from db.repositories.player_repository import PlayerRepository
from services.AdminService import AdminService
from services.PageService import PageService


class DreamerLibraryBot(commands.Bot):
    database: Database

    player_repository: PlayerRepository
    collection_repository: CollectionRepository
    page_repository: PageRepository
    page_alias_repository: PageAliasRepository
    page_image_repository: PageImageRepository
    inventory_repository: InventoryRepository

    admin_service: AdminService
    page_service: PageService

    def __init__(self):

        intents = discord.Intents.default()

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            tree_cls=DreamerCommandTree
        )

    async def setup_hook(self):
        print("Loading extensions...")

        self.database = Database(config.DATABASE)
        await self.database.initialize()

        # Repositories
        self.player_repository = PlayerRepository(self.database)
        self.collection_repository = CollectionRepository(self.database)
        self.page_repository = PageRepository(self.database)
        self.page_alias_repository = PageAliasRepository(self.database)
        self.page_image_repository = PageImageRepository(self.database)
        self.inventory_repository = InventoryRepository(self.database)

        # Services
        self.admin_service = AdminService(
            database=self.database,
            collection_repository=self.collection_repository,
            page_repository=self.page_repository,
            page_image_repository=self.page_image_repository
        )
        self.page_service = PageService(
            page_repository=self.page_repository,
        )

        await self.load_extension("cogs.ping")
        await self.load_extension("cogs.admin")

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