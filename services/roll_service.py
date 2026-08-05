import random

import config
from enums.rarity import Rarity
from exceptions.no_claims_remaining import NoClaimsRemaining
from exceptions.no_rolls_remaining import NoRollsRemaining
from models.roll_result import RollResult
from models.schema.page import Page
from models.schema.player import Player


class RollService:

    def __init__(
            self,
            database,
            player_service,
            player_repository,
            page_repository,
            collection_repository,
            page_image_repository,
            inventory_repository
    ):
        self.database = database

        self.player_service = player_service

        self.player_repository = player_repository
        self.page_repository = page_repository
        self.collection_repository = collection_repository
        self.page_image_repository = page_image_repository
        self.inventory_repository = inventory_repository

    async def roll(
            self,
            discord_user
    ) -> RollResult:

        async with self.database.transaction() as connection:

            #
            # Player
            #

            player = await self.player_service.get_or_create_player(
                discord_user,
                connection
            )

            await self.player_service.refresh_player(
                player,
                connection
            )

            #
            # No rolls left
            #

            if not await self.player_service.use_roll(
                    player,
                    connection
            ):
                raise NoRollsRemaining()

            #
            # Choose rarity
            #

            rarity = random.choices(
                population=[
                    Rarity.SINGLE_STAR,
                    Rarity.DOUBLE_STAR,
                    Rarity.TRIPLE_STAR
                ],
                weights=[
                    config.SINGLE_STAR_DROP_CHANCE,
                    config.DOUBLE_STAR_DROP_CHANCE,
                    config.TRIPLE_STAR_DROP_CHANCE
                ],
                k=1
            )[0]

            #
            # Random page
            #

            page = await self.page_repository.get_random_by_rarity(
                rarity,
                connection
            )

            if page is None:
                raise NoRollsRemaining()

            #
            # Discover the page globally
            #

            if not page.discovered:
                await self.page_repository.discover(
                    page.id,
                    connection
                )

                page.discovered = True

            collection = await self.collection_repository.get(
                page.collection_id,
                connection
            )

            image = await self.page_image_repository.get_main_image(
                page.id,
                connection
            )

            return RollResult(
                page=page,
                collection=collection,
                image=image,
                player=player
            )

    async def claim(
            self,
            player: Player,
            page: Page
    ):

        async with self.database.transaction() as connection:

            #
            # Refresh player
            #

            await self.player_service.refresh_player(
                player,
                connection
            )

            #
            # Consume one claim
            #

            if not await self.player_service.use_claim(
                    player,
                    connection
            ):
                raise NoClaimsRemaining()

            #
            # Become the original owner if nobody has claimed it yet
            #

            if page.owner_id is None:

                claimed = await self.page_repository.claim(
                    page.id,
                    player.discord_id,
                    connection
                )

                if claimed:
                    page.owner_id = player.discord_id

            #
            # Give inventory copy
            #

            await self.inventory_repository.add_page(
                player.discord_id,
                page.id,
                1,
                connection
            )

    async def sell(
            self,
            player: Player,
            rarity: Rarity
    ):

        async with self.database.transaction() as connection:
            gold = config.ROLL_SELL_VALUES[rarity]

            player.gold += gold

            await self.player_repository.update(
                player,
                connection
            )

            return gold