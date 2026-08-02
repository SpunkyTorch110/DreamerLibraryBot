from dataclasses import dataclass

from enums.gender import Gender
from enums.page_type import PageType
from enums.rank import Rank
from enums.rarity import Rarity


@dataclass(slots=True)
class CreatePageRequest:

    name: str

    gender: Gender

    rank: Rank

    rarity: Rarity

    page_type: PageType

    description: str

    collection: str

    image_url: str

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int