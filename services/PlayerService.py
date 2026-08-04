from datetime import datetime, timedelta

import discord

import config
from models.schema.player import Player


class PlayerService:

    ROLL_RECHARGE = timedelta(seconds=config.ROLL_RECHARGE)
    CLAIM_RECHARGE = timedelta(seconds=config.CLAIM_RECHARGE)

    def __init__(self, bot, database, player_repository):
        self.bot = bot
        self.database = database
        self.player_repository = player_repository

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