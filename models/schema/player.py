from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Player:

    discord_id: int

    username: str
    display_name: str | None

    gold: int

    last_roll: datetime | None
    last_claim: datetime | None

    created_at: datetime