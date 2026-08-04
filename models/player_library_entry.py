from dataclasses import dataclass

from enums.rarity import Rarity


@dataclass(slots=True)
class PlayerLibraryEntry:

    page_id: int

    discovered: bool

    name: str | None

    rarity: Rarity | None

    amount: int

    claimed: bool

    original_owner: bool