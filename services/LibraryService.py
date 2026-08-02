from models.collection_progress import CollectionProgress
from models.library_info import LibraryInfo

class LibraryService:

    def __init__(
            self,
            database,
            page_repository,
            player_repository,
            collection_repository,
            inventory_repository
    ):
        self.database = database

        self.page_repository = page_repository
        self.player_repository = player_repository
        self.collection_repository = collection_repository
        self.inventory_repository = inventory_repository

    async def get_library_info(self) -> LibraryInfo:

        async with self.database.transaction() as connection:

            total_pages = await self.page_repository.count(
                connection
            )

            discovered_pages = await self.page_repository.count_discovered(
                connection
            )

            claimed_pages = await self.page_repository.count_claimed(
                connection
            )

            total_players = await self.player_repository.count(
                connection
            )

            total_collections = await self.collection_repository.count(
                connection
            )

            total_copies = await self.inventory_repository.count_total_pages(
                connection
            )

            total_gold = await self.player_repository.total_gold(
                connection
            )

            return LibraryInfo(
                total_pages=total_pages,
                discovered_pages=discovered_pages,
                claimed_pages=claimed_pages,

                total_players=total_players,
                total_collections=total_collections,

                total_copies=total_copies,
                total_gold=total_gold,

                discovery_percentage=(
                    discovered_pages / total_pages * 100
                    if total_pages else 0
                ),

                claim_percentage=(
                    claimed_pages / total_pages * 100
                    if total_pages else 0
                ),

                average_copies_per_page=(
                    total_copies / total_pages
                    if total_pages else 0
                )
            )

    async def get_collection_progress(
            self
    ) -> list[CollectionProgress]:
        async with self.database.transaction() as connection:
            return await self.collection_repository.get_collection_progress(
                connection
            )

    async def get_leaderboards(self):
        async with self.database.transaction() as connection:
            return {
                "pages": await self.player_repository.get_top_pages(
                    connection=connection
                ),
                "claims": await self.player_repository.get_top_first_claims(
                    connection=connection
                ),
                "gold": await self.player_repository.get_top_gold(
                    connection=connection
                )
            }