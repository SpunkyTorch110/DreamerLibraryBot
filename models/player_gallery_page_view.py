from dataclasses import dataclass

from enums.rarity import Rarity
from models.schema.page import Page


@dataclass(slots=True)
class PlayerGalleryPageView:

    page_id: int
    discovered: bool

    name: str
    rarity: Rarity | None

    amount: int

    claimed: bool
    original_owner: bool