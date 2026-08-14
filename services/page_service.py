from db.database import Database
from db.repositories.collection_repository import CollectionRepository
from db.repositories.page_image_repository import PageImageRepository
from db.repositories.page_repository import PageRepository
from models.gallery_page import GalleryPage
from models.library_page_entry import LibraryPageEntry
from models.page_view import PageView

class PageService:

    def __init__(
        self,
        database: Database,
        page_repository: PageRepository,
        collection_repository: CollectionRepository,
        page_image_repository: PageImageRepository
    ):
        self.database = database
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

        async with self.database.transaction() as connection:
            page = await self.page_repository.find_by_name_or_alias(
                search,
                connection
            )

            if page is None:
                return None

            collection = await self.collection_repository.get(
                page.collection_id,
                connection
            )

            image = await self.page_image_repository.get_main_image(
                page.id,
                connection
            )

            return PageView(
                page=page,
                collection=collection,
                image=image
            )

    async def find_discovered_page(
            self,
            search: str
    ) -> PageView | None:

        view = await self.find_page(search)

        if view is None:
            return None

        if not view.page.discovered:
            return None

        return view

    async def get_library_entries(
            self
    ) -> list[LibraryPageEntry]:

        async with self.database.transaction() as connection:
            return await self.page_repository.get_library_entries(
                connection=connection
            )

    async def get_gallery_pages(
            self
    ) -> list[GalleryPage]:

        async with self.database.transaction() as connection:
            return await self.page_repository.get_gallery_pages(
                connection
            )

    async def get_library_entries_by_collection(
            self,
            collection_name: str
    ) -> tuple[str, list[LibraryPageEntry]] | None:

        async with self.database.transaction() as connection:
            collection = await self.collection_repository.find_by_name(
                collection_name,
                connection
            )

            if collection is None:
                return None

            entries = await self.page_repository.get_library_entries_by_collection(
                collection.id,
                connection
            )

            return collection.name, entries