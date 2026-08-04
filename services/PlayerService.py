from datetime import datetime, timedelta

import discord

import config
from models.player_collection_progress import PlayerCollectionProgress
from models.player_library_entry import PlayerLibraryEntry
from models.player_library_view import PlayerLibraryView
from models.player_profile_view import PlayerProfileView
from models.schema.player import Player


class PlayerService:

    ROLL_RECHARGE = timedelta(hours=config.ROLL_RECHARGE)
    CLAIM_RECHARGE = timedelta(hours=config.CLAIM_RECHARGE)

    def __init__(self, bot, database, player_repository, inventory_repository, page_repository, collection_repository):
        self.bot = bot
        self.database = database
        self.player_repository = player_repository
        self.inventory_repository = inventory_repository
        self.page_repository = page_repository
        self.collection_repository = collection_repository


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

        player = await self.player_repository.get(
            discord_user.id,
            connection
        )

        if player is not None:
            return player

        now = datetime.now()

        player = Player(
            discord_id=discord_user.id,

            username=discord_user.name,
            display_name=discord_user.display_name,

            gold=0,

            rolls_remaining=config.STARTING_ROLLS,
            claims_remaining=config.STARTING_CLAIMS,

            next_roll_at=(
                None
                if config.STARTING_ROLLS == config.MAX_ROLLS
                else now + timedelta(hours=config.ROLL_RECHARGE)
            ),

            next_claim_at=(
                None
                if config.STARTING_CLAIMS == config.MAX_CLAIMS
                else now + timedelta(hours=config.CLAIM_RECHARGE)
            ),

            created_at=now
        )

        await self.player_repository.create(
            player,
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
                player.next_roll_at += self.ROLL_RECHARGE

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
                player.next_claim_at += self.CLAIM_RECHARGE

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
        """
        Attempts to consume one roll.

        Returns:
            True if a roll was consumed.
            False if the player has no rolls remaining.
        """

        if player.rolls_remaining <= 0:
            return False

        player.rolls_remaining -= 1

        #
        # Start the recharge timer only when leaving the "full" state.
        #

        if player.next_roll_at is None:
            player.next_roll_at = datetime.now() + self.ROLL_RECHARGE

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
        """
        Attempts to consume one claim.

        Returns:
            True if a claim was consumed.
            False if the player has no claims remaining.
        """

        if player.claims_remaining <= 0:
            return False

        player.claims_remaining -= 1

        #
        # Start the recharge timer only when leaving the "full" state.
        #

        if player.next_claim_at is None:
            player.next_claim_at = datetime.now() + self.CLAIM_RECHARGE

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
            offset: int
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
                tx=connection
            )

            total_pages = await self.page_repository.count(
                connection
            )

            return PlayerLibraryView(
                entries=entries,
                total_pages=total_pages
            )