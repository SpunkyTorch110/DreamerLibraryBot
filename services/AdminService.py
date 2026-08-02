from datetime import datetime

from db.database import Database
from db.repositories.collection_repository import CollectionRepository
from db.repositories.page_image_repository import PageImageRepository
from db.repositories.page_repository import PageRepository
from models.create_page_request import CreatePageRequest
from models.schema import page_image
from models.schema.collection import Collection
from models.schema.page import Page
from models.schema.page_image import PageImage

class AdminService:

    def __init__(
        self,
        database,
        collection_repository,
        page_repository,
        page_image_repository
    ):
        self.database: Database = database
        self.collection_repository: CollectionRepository = collection_repository
        self.page_repository: PageRepository = page_repository
        self.page_image_repository: PageImageRepository = page_image_repository

    async def create_page(
            self,
            request: CreatePageRequest
    ) -> tuple[Page, Collection, PageImage]:

        async with self.database.transaction() as connection:

            existing = await self.page_repository.get_by_name(
                request.name,
                connection
            )

            if existing is not None:
                raise ValueError(
                    f"Page '{request.name}' already exists."
                )

            collection = await self.collection_repository.get_by_name(
                request.collection,
                connection
            )

            if collection is None:
                collection = await self.collection_repository.create(
                    Collection(
                        id=None,
                        name=request.collection,
                        description=None,
                        image_url=None
                    ),
                    connection
                )

            page = await self.page_repository.create(
                Page(
                    id=None,
                    name=request.name,
                    gender=request.gender,
                    rank=request.rank,
                    rarity=request.rarity,
                    page_type=request.page_type,
                    description=request.description,
                    strength=request.strength,
                    dexterity=request.dexterity,
                    constitution=request.constitution,
                    intelligence=request.intelligence,
                    wisdom=request.wisdom,
                    charisma=request.charisma,
                    collection_id=collection.id,
                    owner_id=None,
                    discovered=False,
                    created_at=datetime.now()
                ),
                connection
            )

            page_image = await self.page_image_repository.create(
                PageImage(
                    id=None,
                    page_id=page.id,
                    image_url=request.image_url,
                    display_order=0
                ),
                connection
            )

            return page, collection, page_image

