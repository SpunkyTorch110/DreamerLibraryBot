from dataclasses import dataclass

from models.schema.player import Player


@dataclass(slots=True)
class PlayerProfileView:

    player: Player

    total_pages: int
    unique_pages: int
    first_claims: int

    total_library_pages: int

    completion_percentage: float