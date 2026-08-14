from dataclasses import dataclass

from models.schema.collection import Collection
from models.schema.page import Page
from models.schema.page_image import PageImage


@dataclass(slots=True)
class PageView:

    page: Page

    collection: Collection

    image: PageImage | None

    amount: int = 0