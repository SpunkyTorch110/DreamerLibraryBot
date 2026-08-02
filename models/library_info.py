from dataclasses import dataclass


@dataclass(slots=True)
class LibraryInfo:

    total_pages: int
    discovered_pages: int
    claimed_pages: int

    total_players: int
    total_collections: int

    total_copies: int
    total_gold: int

    average_copies_per_page: float
    discovery_percentage: float
    claim_percentage: float