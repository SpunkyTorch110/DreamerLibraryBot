from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Inventory:

    player_id: int

    page_id: int

    amount: int

    favourite: bool

    first_obtained: datetime