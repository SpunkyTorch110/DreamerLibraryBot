from datetime import datetime

from db.database import Database
from db.repositories.collection_repository import CollectionRepository
from db.repositories.inventory_repository import InventoryRepository
from db.repositories.page_alias_repository import PageAliasRepository
from db.repositories.page_image_repository import PageImageRepository
from db.repositories.page_repository import PageRepository
from models.create_page_request import CreatePageRequest
from models.edit_page_general import EditPageGeneralRequest
from models.edit_page_stats import EditPageStatsRequest
from models.schema import page_image
from models.schema.collection import Collection
from models.schema.page import Page
from models.schema.page_alias import PageAlias
from models.schema.page_image import PageImage

class AdminService:

    def __init__(
        self,
        database,
        collection_repository,
        page_repository,
        page_image_repository,
        page_alias_repository,
        inventory_repository,
    ):
        self.database: Database = database
        self.collection_repository: CollectionRepository = collection_repository
        self.page_repository: PageRepository = page_repository
        self.page_image_repository: PageImageRepository = page_image_repository
        self.page_alias_repository: PageAliasRepository = page_alias_repository
        self.inventory_repository: InventoryRepository = inventory_repository

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

    async def add_page_alias(
            self,
            page_name: str,
            alias: str
    ):

        alias = alias.strip()

        if not alias:
            raise ValueError("Alias cannot be empty.")

        async with self.database.transaction() as connection:

            page = await self.page_repository.get_by_name(
                page_name,
                connection
            )

            if page is None:
                raise ValueError(f"Page '{page_name}' does not exist.")

            exists = await self.page_alias_repository.exists(
                page.id,
                alias,
                connection
            )

            if exists:
                raise ValueError(
                    f"'{alias}' is already an alias of '{page_name}'."
                )

            await self.page_alias_repository.create(
                PageAlias(
                    id=None,
                    page_id=page.id,
                    alias=alias
                ),
                connection
            )

    async def delete_page(
            self,
            page_name: str
    ):

        async with self.database.transaction() as connection:
            page = await self.page_repository.get_by_name(
                page_name,
                connection
            )

            if page is None:
                raise ValueError(
                    f"Page '{page_name}' does not exist."
                )

            await self.page_repository.delete(
                page.id,
                connection
            )

    async def edit_page_general(
            self,
            request: EditPageGeneralRequest
    ) -> Page:

        async with self.database.transaction() as connection:

            page = await self.page_repository.get_by_name(
                request.page_name,
                connection
            )

            if page is None:
                raise ValueError(
                    f"Page '{request.page_name}' does not exist."
                )

            if request.collection is not None:

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

                page.collection_id = collection.id

            if request.new_name is not None:
                page.name = request.new_name.strip()

            if request.gender is not None:
                page.gender = request.gender

            if request.rank is not None:
                page.rank = request.rank

            if request.rarity is not None:
                page.rarity = request.rarity

            if request.page_type is not None:
                page.page_type = request.page_type

            await self.page_repository.update(
                page,
                connection
            )

            return page

    async def edit_page_stats(
            self,
            request: EditPageStatsRequest
    ) -> Page:

        async with self.database.transaction() as connection:

            page = await self.page_repository.get_by_name(
                request.page_name,
                connection
            )

            if page is None:
                raise ValueError(
                    f"Page '{request.page_name}' does not exist."
                )

            if request.strength is not None:
                page.strength = request.strength

            if request.dexterity is not None:
                page.dexterity = request.dexterity

            if request.constitution is not None:
                page.constitution = request.constitution

            if request.intelligence is not None:
                page.intelligence = request.intelligence

            if request.wisdom is not None:
                page.wisdom = request.wisdom

            if request.charisma is not None:
                page.charisma = request.charisma

            await self.page_repository.update(
                page,
                connection
            )

            return page