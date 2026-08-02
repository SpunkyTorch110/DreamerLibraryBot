from db.repositories.page_repository import PageRepository


class PageService:

    def __init__(
        self,
        page_repository: PageRepository
    ):
        self.page_repository = page_repository

    async def get_total_pages(self) -> int:
        """
        Returns the total number of unique pages in the database.
        """
        return await self.page_repository.count()