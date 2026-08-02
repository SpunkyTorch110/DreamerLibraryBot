from datetime import datetime

from db.repositories.base_repository import BaseRepository
from models.schema.inventory import Inventory


class InventoryRepository(BaseRepository):

    def _map_row(self, row):
        return Inventory(
            player_id=row["player_id"],
            page_id=row["page_id"],
            amount=row["amount"],
            favourite=bool(row["favourite"]),
            first_obtained=self.from_database_datetime(
                row["first_obtained"]
            )
        )

    async def get(
            self,
            player_id: int,
            page_id: int,
            tx=None
    ) -> Inventory | None:
        row = await self.fetch_one(
            """
            SELECT *
            FROM inventory
            WHERE player_id = ?
              AND page_id = ?
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

        return None if row is None else self._map_row(row)

    async def get_inventory(
            self,
            player_id: int,
            tx=None
    ) -> list[Inventory]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM inventory
            WHERE player_id = ?
            ORDER BY first_obtained
            """,
            (player_id,),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def exists(
            self,
            player_id: int,
            page_id: int,
            tx=None
    ) -> bool:
        return await self.query_exists(
            """
            SELECT EXISTS(SELECT 1
                          FROM inventory
                          WHERE player_id = ?
                            AND page_id = ?)
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

    async def delete(
            self,
            player_id: int,
            page_id: int,
            tx=None
    ):
        await self.execute(
            """
            DELETE
            FROM inventory
            WHERE player_id = ?
              AND page_id = ?
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

    async def add_page(
            self,
            player_id: int,
            page_id: int,
            amount: int = 1,
            tx=None
    ):
        await self.execute(
            """
            INSERT INTO inventory
            (player_id,
             page_id,
             amount,
             favourite,
             first_obtained)
            VALUES (?, ?, ?, 0, ?) ON CONFLICT(player_id, page_id)

            DO
            UPDATE SET
                amount = amount + excluded.amount
            """,
            (
                player_id,
                page_id,
                amount,
                self.to_database_datetime(datetime.now())
            ),
            tx
        )

    async def remove_page(
            self,
            player_id: int,
            page_id: int,
            amount: int = 1,
            tx=None,
    ):
        await self.execute(
            """
            UPDATE inventory

            SET amount = amount - ?

            WHERE player_id = ?
              AND page_id = ?
            """,
            (
                amount,
                player_id,
                page_id
            ),
            tx
        )

        await self.execute(
            """
            DELETE
            FROM inventory
            WHERE player_id = ?
              AND page_id = ?
              AND amount <= 0
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

    async def set_amount(
            self,
            player_id: int,
            page_id: int,
            amount: int,
            tx=None,
    ):
        await self.execute(
            """
            UPDATE inventory

            SET amount = ?

            WHERE player_id = ?
              AND page_id = ?
            """,
            (
                amount,
                player_id,
                page_id
            ),
            tx
        )

    async def get_amount(
            self,
            player_id: int,
            page_id: int,
            tx=None
    ) -> int:
        row = await self.fetch_one(
            """
            SELECT amount
            FROM inventory
            WHERE player_id = ?
              AND page_id = ?
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

        return 0 if row is None else row["amount"]

    async def set_favourite(
            self,
            player_id: int,
            page_id: int,
            favourite: bool,
            tx=None
    ):
        await self.execute(
            """
            UPDATE inventory

            SET favourite = ?

            WHERE player_id = ?
              AND page_id = ?
            """,
            (
                int(favourite),
                player_id,
                page_id
            ),
            tx
        )

    async def get_favourites(
            self,
            player_id: int,
            tx=None
    ) -> list[Inventory]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM inventory
            WHERE player_id = ?
              AND favourite = 1
            """,
            (player_id,),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def count_unique_pages(
            self,
            player_id: int,
            tx=None
    ) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM inventory
            WHERE player_id = ?
            """,
            (player_id,),
            tx
        )

        return row[0]

    async def count_total_pages(
            self,
            player_id: int,
            tx=None
    ) -> int:
        row = await self.fetch_one(
            """
            SELECT SUM(amount)
            FROM inventory
            WHERE player_id = ?
            """,
            (player_id,),
            tx
        )

        return 0 if row[0] is None else row[0]