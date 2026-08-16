import aiosqlite

from db.repositories.base_repository import BaseRepository
from enums.gender import Gender
from enums.page_type import PageType
from enums.rank import Rank
from enums.rarity import Rarity
from models.gallery_page import GalleryPage
from models.leaderboard_entry import LeaderboardEntry
from models.library_page_entry import LibraryPageEntry
from models.player_gallery_page_view import PlayerGalleryPageView
from models.player_library_entry import PlayerLibraryEntry
from models.schema.collection import Collection
from models.schema.page import Page
from models.schema.page_image import PageImage


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
            tx=None
    ):
        await self.execute(
            """
            UPDATE pages
            SET discovered = 1
            WHERE id = ?
            """,
            (
                page_id,
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

    async def count_claimed(self, tx=None) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM pages
            WHERE owner_id IS NOT NULL
            """,
            (),
            tx
        )

        return row["count"]

    async def get_library_entries(
            self,
            connection=None
    ) -> list[LibraryPageEntry]:
        rows = await self.fetch_all(
            """
            SELECT
                id,
                name,
                rarity,
                discovered,
                owner_id IS NOT NULL AS claimed
            FROM pages
            ORDER BY id
            """,
            (
    
            ),
            connection
        )

        return [
            LibraryPageEntry(
                id=row["id"],
                name=row["name"],
                discovered=bool(row["discovered"]),
                rarity=Rarity(row["rarity"]),
                claimed=bool(row["claimed"])
            )
            for row in rows
        ]

    async def get_gallery_pages(
            self,
            connection=None
    ) -> list[GalleryPage]:

        rows = await self.fetch_all(
            """
            SELECT

                -- Page
                p.id          AS page_id,
                p.name,
                p.gender,
                p.rank,
                p.rarity,
                p.type,
                p.description,
                p.strength,
                p.dexterity,
                p.constitution,
                p.intelligence,
                p.wisdom,
                p.charisma,
                p.collection_id,
                p.owner_id,
                p.discovered,
                p.created_at,

                -- Collection
                c.id          AS collection_id,
                c.name        AS collection_name,
                c.description AS collection_description,
                c.image_url   AS collection_image,

                -- Main Image
                pi.id         AS image_id,
                pi.image_url,
                pi.display_order

            FROM pages p

                     INNER JOIN collections c
                                ON c.id = p.collection_id

                     LEFT JOIN page_images pi
                               ON pi.page_id = p.id
                                   AND pi.display_order = 0

            ORDER BY p.id
            """,
            (),
            connection
        )

        gallery = []

        for row in rows:

            page = Page(
                id=row["page_id"],
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
                created_at=self.from_database_datetime(
                    row["created_at"]
                )
            )

            collection = Collection(
                id=row["collection_id"],
                name=row["collection_name"],
                description=row["collection_description"],
                image_url=row["collection_image"]
            )

            image = None

            if row["image_id"] is not None:
                image = PageImage(
                    id=row["image_id"],
                    page_id=page.id,
                    image_url=row["image_url"],
                    display_order=row["display_order"]
                )

            gallery.append(
                GalleryPage(
                    page=page,
                    collection=collection,
                    image=image
                )
            )

        return gallery

    async def count_first_claims(
            self,
            owner_id: int,
            tx=None
    ) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM pages
            WHERE owner_id = ?
            """,
            (owner_id,),
            tx
        )

        return row[0]

    async def get_player_library_entries(
            self,
            owner_id: int,
            limit: int,
            offset: int,
            collection_id: int | None = None,
            tx=None
    ) -> list[PlayerLibraryEntry]:

        rows = await self.fetch_all(
            """
            SELECT p.id,
                   p.name,
                   p.rarity,
                   p.discovered,
                   p.owner_id,

                   COALESCE(i.amount, 0) AS amount

            FROM pages p

                     LEFT JOIN inventory i
                               ON i.page_id = p.id
                                   AND i.player_id = ?

            WHERE (
                      ? IS NULL
                          OR p.collection_id = ?
                      )

            ORDER BY p.id LIMIT ?
            OFFSET ?
            """,
            (
                owner_id,
                collection_id,
                collection_id,
                limit,
                offset
            ),
            tx
        )

        return [
            PlayerLibraryEntry(
                page_id=row["id"],

                discovered=bool(row["discovered"]),

                name=row["name"],

                rarity=(
                    None
                    if row["rarity"] is None
                    else Rarity(row["rarity"])
                ),

                amount=row["amount"],

                # This should mean "claimed by anyone"
                claimed=row["owner_id"] is not None,

                # This means "this player was the first claimant"
                original_owner=(
                        row["owner_id"] == owner_id
                )
            )
            for row in rows
        ]

    async def get_random_by_rarity(
            self,
            rarity: Rarity,
            tx=None
    ) -> Page | None:

        row = await self.fetch_one(
            """
            SELECT *
            FROM pages
            WHERE rarity = ?
            ORDER BY RANDOM() LIMIT 1
            """,
            (
                int(rarity),
            ),
            tx
        )

        return None if row is None else self._map_row(row)

    async def claim(
            self,
            page_id: int,
            owner_id: int,
            tx=None
    ) -> bool:

        cursor = await self.execute(
            """
            UPDATE pages
            SET owner_id = ?
            WHERE id = ?
              AND owner_id IS NULL
            """,
            (
                owner_id,
                page_id
            ),
            tx
        )

        return cursor.rowcount == 1

    async def get_player_gallery_entries(
            self,
            player_id: int,
            limit: int,
            offset: int,
            tx=None
    ) -> list[PlayerGalleryPageView]:

        rows = await self.fetch_all(
            """
            SELECT p.id,
                   p.name,
                   p.rarity,
                   p.discovered,
                   p.owner_id,

                   i.amount

            FROM pages p

                     INNER JOIN inventory i
                                ON i.page_id = p.id
                                    AND i.player_id = ?

            WHERE i.amount > 0

            ORDER BY p.id LIMIT ?
            OFFSET ?
            """,
            (
                player_id,
                limit,
                offset
            ),
            tx
        )

        return [
            PlayerGalleryPageView(
                page_id=row["id"],

                discovered=bool(row["discovered"]),

                name=row["name"],
                rarity=(
                    None
                    if row["rarity"] is None
                    else Rarity(row["rarity"])
                ),

                amount=row["amount"],

                claimed=row["owner_id"] is not None,

                original_owner=(
                        row["owner_id"] == player_id
                )
            )
            for row in rows
        ]

    async def count_player_library_entries(
            self,
            owner_id: int,
            collection_id: int | None = None,
            tx=None
    ) -> int:

        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM pages p

            WHERE (
                      ? IS NULL
                          OR p.collection_id = ?
                      )
            """,
            (
                collection_id,
                collection_id
            ),
            tx
        )

        return row[0]

    async def count_player_gallery_pages(
            self,
            player_id: int,
            tx=None
    ) -> int:

        row = await self.fetch_one(
            """
            SELECT COUNT(*)
            FROM inventory
            WHERE player_id = ?
              AND amount > 0
            """,
            (
                player_id,
            ),
            tx
        )

        return row[0]

    async def get_player_gallery_page(
            self,
            player_id: int,
            page_id: int,
            tx=None
    ) -> PlayerGalleryPageView | None:

        row = await self.fetch_one(
            """
            SELECT p.id,
                   p.name,
                   p.rarity,
                   p.discovered,
                   p.owner_id,

                   i.amount

            FROM pages p

                     INNER JOIN inventory i
                                ON i.page_id = p.id
                                    AND i.player_id = ?

            WHERE p.id = ?
              AND i.amount > 0
            """,
            (
                player_id,
                page_id
            ),
            tx
        )

        if row is None:
            return None

        return PlayerGalleryPageView(
            page_id=row["id"],

            discovered=bool(row["discovered"]),

            name=row["name"],

            rarity=(
                None
                if row["rarity"] is None
                else Rarity(row["rarity"])
            ),

            amount=row["amount"],

            claimed=row["owner_id"] is not None,

            original_owner=(
                    row["owner_id"] == player_id
            )
        )

    async def get_library_entries_by_collection(
            self,
            collection_id: int,
            tx=None
    ) -> list[LibraryPageEntry]:

        rows = await self.fetch_all(
            """
            SELECT p.id,
                   p.name,
                   p.rarity,
                   p.discovered,
                   p.owner_id

            FROM pages p

            WHERE p.collection_id = ?

            ORDER BY p.id
            """,
            (
                collection_id,
            ),
            tx
        )

        return [
            LibraryPageEntry(
                id=row["id"],
                name=row["name"],
                rarity=(
                    None
                    if row["rarity"] is None
                    else Rarity(row["rarity"])
                ),
                discovered=bool(row["discovered"]),
                claimed=row["owner_id"] is not None
            )
            for row in rows
        ]

    async def count_library_pages(
            self,
            tx=None
    ) -> int:

        row = await self.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM pages
            """,
            (),
            tx
        )

        return row["total"] if row else 0