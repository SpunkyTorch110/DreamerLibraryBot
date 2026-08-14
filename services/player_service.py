from datetime import datetime, timedelta

import discord

import config
from models.page_view import PageView
from models.player_collection_progress import PlayerCollectionProgress
from models.player_gallery_page_view import PlayerGalleryPageView
from models.player_library_view import PlayerLibraryView
from models.player_profile_view import PlayerProfileView
from models.schema.player import Player
from models.schema.player_upgrades import PlayerUpgrades


class PlayerService:

    def __init__(self, bot, database, player_repository, inventory_repository, page_repository, collection_repository, page_image_repository,
                 upgrade_repository, upgrade_service):
        self.bot = bot
        self.database = database
        self.player_repository = player_repository
        self.inventory_repository = inventory_repository
        self.page_repository = page_repository
        self.collection_repository = collection_repository
        self.page_image_repository = page_image_repository
        self.upgrade_repository = upgrade_repository
        self.upgrade_service = upgrade_service


    async def get_discord_user(
            self,
            user_id: int | None
    ) -> discord.User | None:

        if user_id is None:
            return None

        # Try the cache first
        user = self.bot.get_user(user_id)

        if user is not None:
            return user

        # Fetch from Discord if not cached
        try:
            return await self.bot.fetch_user(user_id)
        except discord.NotFound:
            return None
        except discord.HTTPException:
            return None

    async def get_or_create_player(
            self,
            discord_user: discord.User | discord.Member,
            connection=None
    ) -> Player:

        #
        # Check if player already exists
        #

        player = await self.player_repository.get(
            discord_user.id,
            connection
        )

        #
        # Create player if necessary
        #

        if player is None:
            player = Player(
                discord_id=discord_user.id,

                username=discord_user.name,
                display_name=discord_user.display_name,

                gold=0,

                rolls_remaining=3,
                claims_remaining=1,

                next_roll_at=None,
                next_claim_at=None,

                created_at=datetime.now()
            )

            await self.player_repository.create(
                player,
                connection
            )

        #
        # Make sure the player has an upgrades record.
        #
        # This is important because players may have existed
        # before the upgrades system was introduced.
        #

        upgrades = await self.upgrade_repository.get(
            player.discord_id,
            connection
        )

        if upgrades is None:
            await self.upgrade_repository.create(
                PlayerUpgrades(
                    player_id=player.discord_id,

                    roll_upgraded=False,
                    claim_upgraded=False
                ),
                connection
            )

        return player

    async def refresh_player(
            self,
            player: Player,
            connection=None
    ) -> Player:

        now = datetime.now()

        updated = False

        #
        # Rolls
        #

        while (
                player.rolls_remaining < config.MAX_ROLLS
                and player.next_roll_at is not None
                and player.next_roll_at <= now
        ):

            player.rolls_remaining += 1
            updated = True

            if player.rolls_remaining == config.MAX_ROLLS:
                player.next_roll_at = None
            else:

                recharge = await self.get_roll_recharge(
                    player.discord_id,
                    connection
                )

                player.next_roll_at += recharge

        #
        # Claims
        #

        while (
                player.claims_remaining < config.MAX_CLAIMS
                and player.next_claim_at is not None
                and player.next_claim_at <= now
        ):

            player.claims_remaining += 1
            updated = True

            if player.claims_remaining == config.MAX_CLAIMS:
                player.next_claim_at = None
            else:

                recharge = await self.get_claim_recharge(
                    player.discord_id,
                    connection
                )

                player.next_claim_at += recharge

        if updated:
            await self.player_repository.update(
                player,
                connection
            )

        return player

    async def get_active_player(
            self,
            discord_user: discord.User | discord.Member
    ) -> Player:

        async with self.database.transaction() as connection:

            player = await self.get_or_create_player(
                discord_user,
                connection
            )

            #
            # Sync Discord information
            #

            updated = False

            if player.username != discord_user.name:
                player.username = discord_user.name
                updated = True

            if player.display_name != discord_user.display_name:
                player.display_name = discord_user.display_name
                updated = True

            if updated:
                await self.player_repository.update(
                    player,
                    connection
                )

            await self.refresh_player(
                player,
                connection
            )

            return player

    async def use_roll(
            self,
            player: Player,
            connection=None
    ) -> bool:

        if player.rolls_remaining <= 0:
            return False

        player.rolls_remaining -= 1

        if player.next_roll_at is None:
            recharge = await self.get_roll_recharge(
                player.discord_id,
                connection
            )

            player.next_roll_at = datetime.now() + recharge

        await self.player_repository.update(
            player,
            connection
        )

        return True

    async def use_claim(
            self,
            player: Player,
            connection=None
    ) -> bool:

        if player.claims_remaining <= 0:
            return False

        player.claims_remaining -= 1

        if player.next_claim_at is None:
            recharge = await self.get_claim_recharge(
                player.discord_id,
                connection
            )

            player.next_claim_at = datetime.now() + recharge

        await self.player_repository.update(
            player,
            connection
        )

        return True

    async def get_profile(
            self,
            discord_user: discord.User | discord.Member
    ) -> PlayerProfileView:

        player = await self.get_active_player(
            discord_user
        )

        async with self.database.transaction() as connection:
            total_pages = await self.inventory_repository.count_total_player_pages(
                player.discord_id,
                connection
            )

            unique_pages = await self.inventory_repository.count_unique_pages(
                player.discord_id,
                connection
            )

            first_claims = await self.page_repository.count_first_claims(
                player.discord_id,
                connection
            )

            total_library_pages = await self.page_repository.count(
                connection
            )

            return PlayerProfileView(
                player=player,
                total_pages=total_pages,
                unique_pages=unique_pages,
                first_claims=first_claims,
                total_library_pages=total_library_pages,
                completion_percentage=(
                    (unique_pages / total_library_pages) * 100
                    if total_library_pages > 0
                    else 0
                )
            )

    async def get_profile_if_exists(
            self,
            discord_user: discord.User | discord.Member
    ) -> PlayerProfileView | None:

        async with self.database.transaction() as connection:
            player = await self.player_repository.get(
                discord_user.id,
                connection
            )

            if player is None:
                return None

            await self.refresh_player(
                player,
                connection
            )

            total_pages = await self.inventory_repository.count_total_player_pages(
                player.discord_id,
                connection
            )

            unique_pages = await self.inventory_repository.count_unique_pages(
                player.discord_id,
                connection
            )

            first_claims = await self.page_repository.count_first_claims(
                player.discord_id,
                connection
            )

            total_library_pages = await self.page_repository.count(
                connection
            )

            completion_percentage = (
                unique_pages / total_library_pages * 100
                if total_library_pages > 0
                else 0
            )

            return PlayerProfileView(
                player=player,
                total_pages=total_pages,
                unique_pages=unique_pages,
                first_claims=first_claims,
                total_library_pages=total_library_pages,
                completion_percentage=completion_percentage
            )

    async def get_collection_progress(
            self,
            discord_user: discord.User | discord.Member
    ) -> list[PlayerCollectionProgress]:

        async with self.database.transaction() as connection:
            player = await self.get_or_create_player(
                discord_user,
                connection
            )

            await self.refresh_player(
                player,
                connection
            )

            progress = await self.collection_repository.get_player_progress(
                player.discord_id,
                connection
            )

            return [
                PlayerCollectionProgress(
                    collection_id=entry.collection_id,
                    collection_name=entry.collection_name,

                    total_pages=entry.total_pages,
                    collected_pages=entry.collected_pages,
                    claimed_pages=entry.claimed_pages,

                    completion_percentage=(
                        (entry.collected_pages / entry.total_pages) * 100
                        if entry.total_pages > 0
                        else 0
                    )
                )
                for entry in progress
            ]

    async def get_player_library(
            self,
            discord_user: discord.User | discord.Member,
            limit: int,
            offset: int,
            collection_id: int | None = None
    ) -> PlayerLibraryView:

        async with self.database.transaction() as connection:
            player = await self.get_or_create_player(
                discord_user,
                connection
            )

            await self.refresh_player(
                player,
                connection
            )

            entries = await self.page_repository.get_player_library_entries(
                owner_id=player.discord_id,
                limit=limit,
                offset=offset,
                collection_id=collection_id,
                tx=connection
            )

            total_pages = await self.page_repository.count_player_library_entries(
                owner_id=player.discord_id,
                collection_id=collection_id,
                tx=connection
            )

            return PlayerLibraryView(
                entries=entries,
                total_pages=total_pages
            )

    async def get_player_gallery_entries(
            self,
            discord_user: discord.User | discord.Member,
            limit: int,
            offset: int
    ) -> tuple[list[PlayerGalleryPageView], int]:

        async with self.database.transaction() as connection:
            #
            # Make sure the player has a profile.
            #

            player = await self.get_or_create_player(
                discord_user,
                connection
            )

            #
            # Get the player's owned pages.
            #

            entries = await self.page_repository.get_player_gallery_entries(
                player_id=player.discord_id,
                limit=limit,
                offset=offset,
                tx=connection
            )

            #
            # Get the total number of unique pages owned.
            #

            total = await self.page_repository.count_player_gallery_pages(
                player_id=player.discord_id,
                tx=connection
            )

            return entries, total

    async def get_player_gallery_page(
            self,
            discord_user: discord.User | discord.Member,
            page_id: int
    ) -> PageView | None:

        async with self.database.transaction() as connection:

            player = await self.get_or_create_player(
                discord_user,
                connection
            )

            entry = await self.page_repository.get_player_gallery_page(
                player_id=player.discord_id,
                page_id=page_id,
                tx=connection
            )

            if entry is None:
                return None

            page = await self.page_repository.get(
                entry.page_id,
                connection
            )

            if page is None:
                return None

            collection = await self.collection_repository.get(
                page.collection_id,
                connection
            )

            image = await self.page_image_repository.get_main_image(
                page.id,
                connection
            )

            return PageView(
                page=page,
                collection=collection,
                image=image,
                amount=entry.amount
            )

    async def get_player_recharge_times(
            self,
            player_id: int,
            connection=None
    ) -> tuple[timedelta, timedelta]:

        upgrades = await self.upgrade_repository.get(
            player_id,
            connection
        )

        roll_recharge = (
            config.ROLL_RECHARGE_UPGRADED
            if upgrades and upgrades.roll_upgraded
            else config.ROLL_RECHARGE
        )

        claim_recharge = (
            config.CLAIM_RECHARGE_UPGRADED
            if upgrades and upgrades.claim_upgraded
            else config.CLAIM_RECHARGE
        )

        return roll_recharge, claim_recharge

    async def get_roll_recharge(
            self,
            player_id: int,
            connection=None
    ):
        return await self.upgrade_service.get_roll_recharge(
            player_id,
            connection
        )

    async def get_claim_recharge(
            self,
            player_id: int,
            connection=None
    ):
        return await self.upgrade_service.get_claim_recharge(
            player_id,
            connection
        )