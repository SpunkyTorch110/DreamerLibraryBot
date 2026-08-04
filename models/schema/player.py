from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Player:

    discord_id: int

    username: str
    display_name: str | None

    gold: int

    rolls_remaining: int
    claims_remaining: int

    next_roll_at: datetime | None
    next_claim_at: datetime | None

    created_at: datetime