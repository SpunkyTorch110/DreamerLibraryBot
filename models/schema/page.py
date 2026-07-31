from dataclasses import dataclass
from datetime import datetime

from enums.gender import Gender
from enums.rank import Rank
from enums.rarity import Rarity
from enums.page_type import PageType


@dataclass(slots=True)
class Page:

    id: int | None

    name: str

    gender: Gender

    rank: Rank

    rarity: Rarity

    page_type: PageType

    description: str | None

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    collection_id: int | None

    owner_id: int | None

    discovered: bool

    created_at: datetime