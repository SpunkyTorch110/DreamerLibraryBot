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
from db.repositories.upgrade_repository import UpgradeRepository
from services.admin_service import AdminService
from services.library_service import LibraryService
from services.page_service import PageService
from services.player_service import PlayerService
from services.roll_service import RollService
from services.upgrade_service import UpgradeService


class DreamerLibraryBot(commands.Bot):
    database: Database

    player_repository: PlayerRepository
    collection_repository: CollectionRepository
    page_repository: PageRepository
    page_alias_repository: PageAliasRepository
    page_image_repository: PageImageRepository
    inventory_repository: InventoryRepository
    upgrade_repository: UpgradeRepository

    admin_service: AdminService
    page_service: PageService
    player_service: PlayerService
    library_service: LibraryService
    roll_service: RollService
    upgrade_service: UpgradeService

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
        self.upgrade_repository = UpgradeRepository(self.database)

        # Services
        self.admin_service = AdminService(
            database=self.database,
            collection_repository=self.collection_repository,
            page_repository=self.page_repository,
            page_image_repository=self.page_image_repository,
            page_alias_repository=self.page_alias_repository,
            inventory_repository=self.inventory_repository
        )
        self.page_service = PageService(
            database=self.database,
            page_repository=self.page_repository,
            collection_repository=self.collection_repository,
            page_image_repository=self.page_image_repository,
        )
        self.player_service = PlayerService(
            bot=self,
            database=self.database,
            player_repository=self.player_repository,
            inventory_repository=self.inventory_repository,
            page_repository=self.page_repository,
            collection_repository=self.collection_repository,
            page_image_repository=self.page_image_repository,
            upgrade_repository=self.upgrade_repository,
            upgrade_service=self.upgrade_service,
        )
        self.library_service = LibraryService(
            database=self.database,
            page_repository=self.page_repository,
            player_repository=self.player_repository,
            collection_repository=self.collection_repository,
            inventory_repository=self.inventory_repository,
        )
        self.roll_service = RollService(
            database=self.database,
            player_service=self.player_service,
            player_repository=self.player_repository,
            page_repository=self.page_repository,
            collection_repository=self.collection_repository,
            page_image_repository=self.page_image_repository,
            inventory_repository=self.inventory_repository,
        )
        self.upgrade_service = UpgradeService(
            database=self.database,
            player_service=self.player_service,
            player_repository=self.player_repository,
            upgrade_repository=self.upgrade_repository,
        )

        await self.load_extension("cogs.ping")
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.library")
        await self.load_extension("cogs.pages")
        await self.load_extension("cogs.player")
        await self.load_extension("cogs.roll")
        await self.load_extension("cogs.help")
        await self.load_extension("cogs.bot")

        print("Syncing slash commands...")
        await self.tree.sync()

        print("DreamerLibraryBot is ready.")

    async def on_ready(self):
        await self.change_presence(
            activity=discord.CustomActivity(
                name=config.DISCORD_STATUS
            ),
            status=discord.Status.online
        )

        print(f"Logged in as {self.user}")

async def main():
    bot = DreamerLibraryBot()

    async with bot:
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())