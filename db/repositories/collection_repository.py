from db.repositories.base_repository import BaseRepository

from models.schema.collection import Collection

import aiosqlite

class CollectionRepository(BaseRepository):

    @staticmethod
    def _map_row(row: aiosqlite.Row) -> Collection:
        return Collection(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            image_url=row["image_url"]
        )

    async def create(self, collection: Collection, tx=None) -> Collection:
        cursor = await self.execute(
            """
            INSERT INTO collections
            (
                name,
                description,
                image_url
            )
            VALUES (?, ?, ?)
            """,
            (
                collection.name,
                collection.description,
                collection.image_url
            ),
            tx
        )

        collection.id = cursor.lastrowid

        return collection

    async def get(self, collection_id: int, tx=None) -> Collection | None:

        row = await self.fetch_one(
            """
            SELECT *
            FROM collections
            WHERE id = ?
            """,
            (collection_id,),
            tx
        )

        return None if row is None else self._map_row(row)

    async def get_by_name(self, name: str, tx=None) -> Collection | None:

        row = await self.fetch_one(
            """
            SELECT *
            FROM collections
            WHERE name = ?
            """,
            (name,),
            tx
        )

        return None if row is None else self._map_row(row)

    async def exists(self, collection_id: int, tx=None) -> bool:

        return await self.query_exists(
            """
            SELECT EXISTS(
                SELECT 1
                FROM collections
                WHERE id = ?
            )
            """,
            (collection_id,),
            tx
        )

    async def get_all(self, tx=None) -> list[Collection]:

        rows = await self.fetch_all(
            """
            SELECT *
            FROM collections
            ORDER BY name
            """,
            tx
        )

        return [self._map_row(row) for row in rows]

    async def update(self, collection: Collection, tx=None):

        await self.execute(
            """
            UPDATE collections
            SET
                name = ?,
                description = ?,
                image_url = ?
            WHERE id = ?
            """,
            (
                collection.name,
                collection.description,
                collection.image_url,
                collection.id
            ),
            tx
        )

    async def delete(self, collection_id: int, tx=None):

        await self.execute(
            """
            DELETE
            FROM collections
            WHERE id = ?
            """,
            (collection_id,),
            tx
        )

    async def get_page_count(self, collection_id: int, tx=None) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM pages
            WHERE collection_id = ?
            """,
            (collection_id,),
            tx
        )

        return row[0]