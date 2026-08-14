from datetime import timedelta

from discord import Member, User

import config
from exceptions.insufficient_gold import InsufficientGold
from exceptions.upgrade_already_purchased import UpgradeAlreadyPurchased


class UpgradeService:

    def __init__(
            self,
            database,
            player_service,
            player_repository,
            upgrade_repository
    ):
        self.database = database

        self.player_service = player_service
        self.player_repository = player_repository
        self.upgrade_repository = upgrade_repository

    async def purchase_upgrade(
            self,
            discord_user: User | Member,
            upgrade: str
    ) -> tuple[int, int]:

        async with self.database.transaction() as connection:

            #
            # Get or create player.
            #
            # This also guarantees that an upgrades row exists
            # for old players.
            #

            player = await self.player_service.get_or_create_player(
                discord_user,
                connection
            )

            #
            # Refresh player so that we have the latest gold.
            #

            await self.player_service.refresh_player(
                player,
                connection
            )

            #
            # Get current upgrade state.
            #

            upgrades = await self.upgrade_repository.get(
                player.discord_id,
                connection
            )

            if upgrades is None:
                raise RuntimeError(
                    "Player upgrades not found."
                )

            #
            # Determine the upgrade and its cost.
            #

            if upgrade == "roll":

                if upgrades.roll_upgraded:
                    raise UpgradeAlreadyPurchased()

                cost = config.ROLL_UPGRADE_COST

            elif upgrade == "claim":

                if upgrades.claim_upgraded:
                    raise UpgradeAlreadyPurchased()

                cost = config.CLAIM_UPGRADE_COST

            else:

                raise ValueError(
                    f"Unknown upgrade: {upgrade}"
                )

            #
            # Check player's gold.
            #

            if player.gold < cost:
                raise InsufficientGold()

            #
            # Deduct gold.
            #

            player.gold -= cost

            await self.player_repository.update(
                player,
                connection
            )

            #
            # Activate the upgrade.
            #

            if upgrade == "roll":

                success = await self.upgrade_repository.upgrade_roll(
                    player.discord_id,
                    connection
                )

            else:

                success = await self.upgrade_repository.upgrade_claim(
                    player.discord_id,
                    connection
                )

            #
            # The database prevents purchasing an upgrade
            # that has already been purchased.
            #

            if not success:
                raise UpgradeAlreadyPurchased()

            return cost, player.gold

    async def get_roll_recharge(
            self,
            player_id: int,
            connection=None
    ) -> timedelta:

        upgrades = await self.upgrade_repository.get(
            player_id,
            connection
        )

        if upgrades is not None and upgrades.roll_upgraded:
            return config.ROLL_RECHARGE_UPGRADED

        return config.ROLL_RECHARGE

    async def get_claim_recharge(
            self,
            player_id: int,
            connection=None
    ) -> timedelta:

        upgrades = await self.upgrade_repository.get(
            player_id,
            connection
        )

        if upgrades is not None and upgrades.claim_upgraded:
            return config.CLAIM_RECHARGE_UPGRADED

        return config.CLAIM_RECHARGE