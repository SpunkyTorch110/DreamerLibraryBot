from dataclasses import dataclass

from enums.gender import Gender
from enums.page_type import PageType
from enums.rank import Rank
from enums.rarity import Rarity


@dataclass(slots=True)
class EditPageGeneralRequest:

    page_name: str

    new_name: str | None = None

    gender: Gender | None = None

    rank: Rank | None = None

    rarity: Rarity | None = None

    page_type: PageType | None = None

    collection: str | None = None