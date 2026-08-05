from dataclasses import dataclass

from models.schema.collection import Collection
from models.schema.page import Page
from models.schema.page_image import PageImage
from models.schema.player import Player


@dataclass(slots=True)
class RollResult:

    page: Page

    collection: Collection

    image: PageImage

    player: Player