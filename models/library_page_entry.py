from dataclasses import dataclass

from enums.rarity import Rarity


@dataclass(slots=True)
class LibraryPageEntry:

    id: int

    name: str

    discovered: bool

    rarity: Rarity

    claimed: bool