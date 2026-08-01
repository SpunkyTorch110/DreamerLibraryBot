import aiosqlite

from db.repositories.base_repository import BaseRepository
from models.schema.page_alias import PageAlias

class PageAliasRepository(BaseRepository):

    @staticmethod
    def _map_row(row: aiosqlite.Row) -> PageAlias:
        return PageAlias(
            id=row["id"],
            page_id=row["page_id"],
            alias=row["alias"]
        )

    async def create(self, page_alias: PageAlias):
        await self.execute(
            """
            INSERT INTO page_aliases
            (page_id,
             alias)
            VALUES (?, ?)
            """,
            (
                page_alias.page_id,
                page_alias.alias
            )
        )

    async def get(
            self,
            alias_id: int
    ) -> PageAlias | None:
        row = await self.fetch_one(
            """
            SELECT *
            FROM page_aliases
            WHERE id = ?
            """,
            (alias_id,)
        )

        return None if row is None else self._map_row(row)

    async def exists(
            self,
            alias: str
    ) -> bool:
        return await self.query_exists(
            """
            SELECT EXISTS(SELECT 1
                          FROM page_aliases
                          WHERE LOWER(alias) = LOWER(?))
            """,
            (alias,)
        )

    async def get_by_page(
            self,
            page_id: int
    ) -> list[PageAlias]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM page_aliases
            WHERE page_id = ?
            ORDER BY alias
            """,
            (page_id,)
        )

        return [self._map_row(row) for row in rows]

    async def search(
            self,
            text: str
    ) -> list[PageAlias]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM page_aliases
            WHERE LOWER(alias)
                      LIKE LOWER(?)
            ORDER BY alias
            """,
            (f"%{text}%",)
        )

        return [self._map_row(row) for row in rows]

    async def update(self, page_alias: PageAlias):
        await self.execute(
            """
            UPDATE page_aliases
            SET alias = ?
            WHERE id = ?
            """,
            (
                page_alias.alias,
                page_alias.id
            )
        )

    async def delete(
            self,
            alias_id: int
    ):
        await self.execute(
            """
            DELETE
            FROM page_aliases
            WHERE id = ?
            """,
            (alias_id,)
        )

    async def delete_by_page(
            self,
            page_id: int
    ):
        await self.execute(
            """
            DELETE
            FROM page_aliases
            WHERE page_id = ?
            """,
            (page_id,)
        )

    async def count(
            self,
            page_id: int
    ) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM page_aliases
            WHERE page_id = ?
            """,
            (page_id,)
        )

        return row[0]