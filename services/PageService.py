from db.repositories.collection_repository import CollectionRepository
from db.repositories.page_image_repository import PageImageRepository
from db.repositories.page_repository import PageRepository
from models.page_view import PageView


class PageService:

    def __init__(
        self,
        page_repository: PageRepository,
        collection_repository: CollectionRepository,
        page_image_repository: PageImageRepository
    ):
        self.page_repository = page_repository
        self.collection_repository = collection_repository
        self.page_image_repository = page_image_repository

    async def get_total_pages(self) -> int:
        """
        Returns the total number of unique pages in the database.
        """
        return await self.page_repository.count()

    async def find_page(
            self,
            search: str
    ) -> PageView | None:

        page = await self.page_repository.find_by_name_or_alias(search)

        if page is None:
            return None

        collection = await self.collection_repository.get(page.collection_id)

        image = await self.page_image_repository.get_main_image(page.id)

        return PageView(
            page=page,
            collection=collection,
            image=image
        )