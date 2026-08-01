import aiosqlite

from db.repositories.base_repository import BaseRepository
from models.schema.page_image import PageImage

class PageImageRepository(BaseRepository):

    @staticmethod
    def _map_row(row: aiosqlite.Row) -> PageImage:
        return PageImage(
            id=row["id"],
            page_id=row["page_id"],
            image_url=row["image_url"],
            display_order=row["display_order"]
        )

    async def create(
            self,
            image: PageImage
    ):
        await self.execute(
            """
            INSERT INTO page_images
            (page_id,
             image_url,
             display_order)
            VALUES (?, ?, ?)
            """,
            (
                image.page_id,
                image.image_url,
                image.display_order
            )
        )

    async def get(
            self,
            image_id: int
    ) -> PageImage | None:
        row = await self.fetch_one(
            """
            SELECT *
            FROM page_images
            WHERE id = ?
            """,
            (image_id,)
        )

        return None if row is None else self._map_row(row)

    async def exists(
            self,
            image_id: int
    ) -> bool:
        return await self.query_exists(
            """
            SELECT EXISTS(SELECT 1
                          FROM page_images
                          WHERE id = ?)
            """,
            (image_id,)
        )

    async def get_by_page(
            self,
            page_id: int
    ) -> list[PageImage]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM page_images
            WHERE page_id = ?
            ORDER BY display_order
            """,
            (page_id,)
        )

        return [self._map_row(row) for row in rows]

    async def get_primary(
            self,
            page_id: int
    ) -> PageImage | None:
        row = await self.fetch_one(
            """
            SELECT *
            FROM page_images
            WHERE page_id = ?
            ORDER BY display_order LIMIT 1
            """,
            (page_id,)
        )

        return None if row is None else self._map_row(row)

    async def update(
            self,
            image: PageImage
    ):
        await self.execute(
            """
            UPDATE page_images
            SET image_url     = ?,
                display_order = ?
            WHERE id = ?
            """,
            (
                image.image_url,
                image.display_order,
                image.id
            )
        )

    async def delete(
            self,
            image_id: int
    ):
        await self.execute(
            """
            DELETE
            FROM page_images
            WHERE id = ?
            """,
            (image_id,)
        )

    async def delete_by_page(
            self,
            page_id: int
    ):
        await self.execute(
            """
            DELETE
            FROM page_images
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
            FROM page_images
            WHERE page_id = ?
            """,
            (page_id,)
        )

        return row[0]