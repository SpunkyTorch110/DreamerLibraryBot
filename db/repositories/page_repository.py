import aiosqlite

from db.repositories.base_repository import BaseRepository
from enums.gender import Gender
from enums.page_type import PageType
from enums.rank import Rank
from enums.rarity import Rarity
from models.schema.page import Page

class PageRepository(BaseRepository):

    def _map_row(self, row: aiosqlite.Row) -> Page:
        return Page(
            id=row["id"],
            name=row["name"],
            gender=Gender(row["gender"]),
            rank=Rank(row["rank"]),
            rarity=Rarity(row["rarity"]),
            page_type=PageType(row["type"]),
            description=row["description"],
            strength=row["strength"],
            dexterity=row["dexterity"],
            constitution=row["constitution"],
            intelligence=row["intelligence"],
            wisdom=row["wisdom"],
            charisma=row["charisma"],
            collection_id=row["collection_id"],
            owner_id=row["owner_id"],
            discovered=bool(row["discovered"]),
            created_at=self.from_database_datetime(row["created_at"])
        )

    async def create(self, page: Page, tx=None) -> Page:
        cursor = await self.execute(
            """
            INSERT INTO pages
            (name,
            gender,
            rank,
            rarity,
            type,
            description,
            strength,
            dexterity,
            constitution,
            intelligence,
            wisdom,
            charisma,
            collection_id,
            owner_id,
            discovered,
            created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                page.name,
                int(page.gender),
                int(page.rank),
                int(page.rarity),
                int(page.page_type),
                page.description,
                page.strength,
                page.dexterity,
                page.constitution,
                page.intelligence,
                page.wisdom,
                page.charisma,
                page.collection_id,
                page.owner_id,
                int(page.discovered),
                self.to_database_datetime(page.created_at)
            ),
            tx
        )

        page.id = cursor.lastrowid

        return page

    async def get(self, page_id: int, tx=None) -> Page | None:
        row = await self.fetch_one(
            """
            SELECT *
            FROM pages
            WHERE id = ?
            """,
            (page_id,),
            tx
        )

        return None if row is None else self._map_row(row)

    async def get_by_name(self, name: str, tx=None) -> Page | None:
        row = await self.fetch_one(
            """
            SELECT *
            FROM pages
            WHERE name = ?
            """,
            (name,),
            tx
        )

        return None if row is None else self._map_row(row)

    async def exists(self, page_id: int, tx=None) -> bool:
        return await self.query_exists(
            """
            SELECT EXISTS(SELECT 1
                          FROM pages
                          WHERE id = ?)
            """,
            (page_id,),
            tx
        )

    async def update(self, page: Page, tx=None):
        await self.execute(
            """
            UPDATE pages
            SET name = ?,
                gender = ?,
                rank = ?,
                rarity = ?,
                type = ?,
                description = ?,
                strength = ?,
                dexterity = ?,
                constitution = ?,
                intelligence = ?,
                wisdom = ?,
                charisma = ?,
                collection_id = ?,
                owner_id = ?,
                discovered = ?
            WHERE id = ?
            """,
            (
                page.name,
                int(page.gender),
                int(page.rank),
                int(page.rarity),
                int(page.page_type),
                page.description,
                page.strength,
                page.dexterity,
                page.constitution,
                page.intelligence,
                page.wisdom,
                page.charisma,
                page.collection_id,
                page.owner_id,
                int(page.discovered),
                page.id
            ),
            tx
        )

    async def delete(self, page_id: int, tx=None):
        await self.execute(
            """
            DELETE
            FROM pages
            WHERE id = ?
            """,
            (page_id,),
            tx
        )

    async def get_all(self, tx=None) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            ORDER BY name
            """,
            (),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def get_by_collection(
            self,
            collection_id: int,
            tx=None
    ) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            WHERE collection_id = ?
            ORDER BY name
            """,
            (collection_id,),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def get_by_rarity(
            self,
            rarity: Rarity,
            tx=None
    ) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            WHERE rarity = ?
            ORDER BY name
            """,
            (int(rarity),),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def get_by_rank(
            self,
            rank: Rank,
            tx=None
    ) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            WHERE rank = ?
            ORDER BY name
            """,
            (int(rank),),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def get_by_type(
            self,
            page_type: PageType,
            tx=None
    ) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            WHERE type = ?
            ORDER BY name
            """,
            (int(page_type),),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def count(self, tx=None) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM pages
            """,
            (),
            tx
        )

        return row[0]

    async def count_discovered(self, tx=None) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM pages
            WHERE discovered = 1
            """,
            (),
            tx
        )

        return row[0]

    async def count_by_collection(
            self,
            collection_id: int,
            tx=None
    ) -> int:
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

    async def set_owner(
            self,
            page_id: int,
            player_id: int,
            tx=None
    ):
        await self.execute(
            """
            UPDATE pages
            SET owner_id = ?
            WHERE id = ?
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

    async def discover(
            self,
            page_id: int,
            player_id: int,
            tx=None
    ):
        await self.execute(
            """
            UPDATE pages
            SET discovered = 1,
                owner_id   = ?
            WHERE id = ?
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

    async def is_discovered(
            self,
            page_id: int,
            tx=None
    ) -> bool:
        return await self.query_exists(
            """
            SELECT EXISTS(SELECT 1
                          FROM pages
                          WHERE id = ?
                            AND discovered = 1)
            """,
            (page_id,),
            tx
        )

    async def get_all_discovered(self, tx=None) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            WHERE discovered = 1
            ORDER BY name
            """,
            (),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def get_all_undiscovered(self, tx=None) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            WHERE discovered = 0
            ORDER BY name
            """,
            (),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def get_by_owner(
            self,
            player_id: int,
            tx=None
    ) -> list[Page]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM pages
            WHERE owner_id = ?
            ORDER BY name
            """,
            (player_id,),
            tx
        )

        return [self._map_row(row) for row in rows]

    async def find_by_name_or_alias(
            self,
            search: str,
            tx=None
    ) -> Page | None:
        row = await self.fetch_one(
            """
            SELECT DISTINCT p.*
            FROM pages p
                     LEFT JOIN page_aliases pa
                               ON pa.page_id = p.id
            WHERE p.name = ?
               OR pa.alias = ? LIMIT 1
            """,
            (
                search,
                search
            ),
            tx
        )

        return None if row is None else self._map_row(row)